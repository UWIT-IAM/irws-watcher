#
# Handle affiliations changes for a netid
#

import base64
import string
import time
import re
import sys
import json
import xml.etree.ElementTree as ET
import logging.config

from resttools.exceptions import DataFailureException

# these must be set by importer
logger = None
irws = None
gws = None

# utility rollup of exceptions
class PersonRegException(Exception):
    pass



# note eduperson affiliation 'alum', 'library-walk-in' not used by gws system
# alumni collected in uw_affiliation_alumni
affiliation_filters = []
eduperson_groups = {'uw_faculty', 'uw_student', 'uw_staff', 'uw_member', 'uw_affiliate', 'uw_employee'}
affiliation_groups = set()

# Process the PersonReg config file

def _get_values(filter, name):
    ret = set()
    ele = filter.find(name)
    if ele is not None:
        for e_value in ele.iter('value'):
            ret.add(e_value.text)
    return ret


def parse_filter_file(filename):
    global affiliation_filters
    affiliation_filters = []
    try:
        defs = ET.parse(filename).getroot()
        for e_group in defs.iter('group'):
            group = {}
            group['cn'] = e_group.attrib['cn']
            affiliation_groups.add(e_group.attrib['cn'])
            e_filter = e_group.find('.//filter')
            if e_filter.attrib['type'] == '1':
                group['cat-status'] = _get_values(e_filter, 'category-status')
                group['sdb-status'] = _get_values(e_filter, 'sdb-sdb_status')
                group['sdb-class'] = _get_values(e_filter, 'sdb-sdb_class')
                group['sdb-branch'] = _get_values(e_filter, 'sdb-branch')
                group['cas-dept'] = _get_values(e_filter, 'cascadia-department')
                group['adv-status'] = _get_values(e_filter, 'advance-status_code')
                group['adv-alum'] = _get_values(e_filter, 'advance-alumni_member')
            affiliation_filters.append(group)
    except Exception as e:
        raise PersonRegException(str(e))

    # logger.info('affiliation processor loaded %d filter definitions.' % (len(affiliation_filters)))
    return affiliation_filters


#
# figure out which affiliations a user should have and correct gws as needed
# returns (adds, dels)
# adds = group cns the user was added to 
# dels = group cns the user was removed from
#

def process_affiliations_as_needed(netid, do_adds=True, do_deletes=True):

    logger.debug('processing ' + netid)
    groups = set()

    # gather info on this person
    try:
        person = irws.get_person(netid=netid)
    except DataFailureException as e:
        logger.info('data failure to get_person.  Will retry.')
        person = irws.get_person(netid=netid)
        logger.info('get_person ok.')

    # category-status
    cat_status = set()
    cats = irws.get_categories(netid=netid)
    for cat in cats.categories:
        cat_status.add(cat['category_code'] + '-' + cat['status_code'])
    sdb_status = set()
    sdb_class = set()
    sdb_branch = set()
    cas_dept = set()
    adv_status = set()
    adv_alum = set()
    idents = person.identifiers
    if type(idents).__name__ == 'dict':
        idents = [idents]
    for ident in idents:
        for k, url in ident.items():
            # logger.debug('doing ' + url)
            if k == 'sdb':
                p = url.find('/sdb/') + 5
                sdb = irws.get_sdb_person(url[p:])
                sdb_status.add(sdb.status_code)
                sdb_class.add(sdb.sdb_class)
                sdb_branch.add(sdb.branch)
            if k == 'cascadia':
                p = url.find('/cascadia/') + 10
                cas = irws.get_cascadia_person(url[p:])
                cas_dept.add(cas.department)
            if k == 'advance':
                p = url.find('/advance/') + 9
                adv = irws.get_advance_person(url[p:])
                adv_status.add(adv.status_code)
                adv_alum.add(adv.alumni_member)

    # compare to affiliation filters
    for filter in affiliation_filters:
        if len(filter['cat-status']) > 0 and not (filter['cat-status'] & cat_status):
            continue
        if len(filter['sdb-status']) > 0 and not (filter['sdb-status'] & sdb_status):
            continue
        if len(filter['sdb-class']) > 0 and not (filter['sdb-class'] & sdb_class):
            continue
        if len(filter['sdb-branch']) > 0 and not (filter['sdb-branch'] & sdb_branch):
            continue
        if len(filter['cas-dept']) > 0 and not (filter['cas-dept'] & cas_dept):
            continue
        if len(filter['adv-status']) > 0 and not (filter['adv-status'] & adv_status):
            continue
        if len(filter['adv-alum']) > 0 and not (filter['adv-alum'] & adv_alum):
            continue

        # user is in this group
        # logger.debug('adding group ' + filter['cn'])
        groups.add(filter['cn'])

    # add eduperson affiliations
    pds = irws.get_pdsentry_by_netid(netid)
    if pds is not None:
        for aff in pds.edupersonaffiliation:
            logger.debug('adding eduperson group uw_' + aff)
            groups.add('uw_' + aff)

    # fix GWS as needed
    adds = set()
    dels = set()
    if do_adds:
        for cn in groups:
            if gws.is_direct_member(cn, netid):
                logger.debug('group %s is ok' % cn )
                continue
            logger.debug('group %s adding member' % cn )
            # ret = gws.put_members(cn, [netid])
            # logger.debug (ret)
            adds.add(cn)

    if do_deletes:
        for cn in eduperson_groups.union(affiliation_groups):
            if cn in groups:
                continue
            if not gws.is_direct_member(cn, netid):
                continue
            logger.debug('group %s adding member' % cn )
            # ret = gws.put_members(cn, [netid])
            # logger.debug (ret)
            dels.add(cn)

    return (adds, dels)
