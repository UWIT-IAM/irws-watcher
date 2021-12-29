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

def process_affiliations_as_needed(netid, do_adds=True, do_rems=False):

    logger.debug('processing ' + netid)
    groups = set()

    # gather info on this person
    try:
        person = irws.get_person(netid=netid)
    except DataFailureException as e:
        logger.info('data failure to get_person.  Will retry.')
        person = irws.get_person(netid=netid)
        logger.info('get_person ok.')

    if person is None:
        logger.info('no person entry for ' + netid)
        return (0, 0)

    # category-status
    cat_status = set()
    cats = irws.get_categories(netid=netid)
    if cats is not None:
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
            if k == 'sdb':
                p = url.find('/sdb/') + 5
                sdb = irws.get_sdb_person(url[p:])

                sdb_status.add(sdb.sdb_status)

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

        # validate user is in this group
        logger.debug('..validate membership of ' + filter['cn'])
        groups.add(filter['cn'])

    # add eduperson affiliations
    pds = irws.get_pdsentry_by_netid(netid)
    if pds is not None:
        for aff in pds.edupersonaffiliation:
            cn = 'uw_' + aff
            if cn in eduperson_groups:
                logger.debug('%s is edumember: %s' % (netid, cn))
                groups.add(cn)

    # fix GWS as needed
    adds = set()
    dels = set()

    is_active = True
    au = irws.get_account_uwnetid(netid=netid)
    if au is not None:
        if au.status_code=='30':
            logger.debug('uwnetid %s is active' % (netid))
        else:
            logger.debug('uwnetid %s is not active' % (netid))
            is_active = False
    try:
        in_groups = gws.search_groups(member=netid, stem='uw_affiliation', scope='all') + \
                    gws.search_groups(member=netid, stem='uw', scope='one') + \
                    gws.search_groups(member=netid, stem='u_uwnetid', scope='one')
        logger.debug('%d existing base groups for %s' % (len(in_groups), netid))
        in_cns = set()
        for g in in_groups:
            if g.name == 'uw_affiliation_staff-non-uwm-workforce':
               continue
            in_cns.add(g.name)

        # remove inactive netid from all affiliations
        if not is_active:
            for cn in in_cns:
                if do_rems:
                    logger.info('removing %s from group %s' % (netid, cn))
                    ret = gws.delete_members(cn, [netid])
                    # logger.info(ret)
                    dels.add(cn)
                else:
                    logger.info('would remove from group %s' % cn)
            return (adds, dels)

        # adds
        for cn in groups:
            if cn in in_cns:
                logger.debug('%s is already in %s' % (netid, cn))
                continue
            if do_adds:
                logger.info('adding %s to group %s' % (netid, cn))
                ret = gws.put_members(cn, [netid])
                # logger.info(ret)
                adds.add(cn)
            else:
                logger.debug('would add %s to group %s' % (netid, cn))

        # removals
        for cn in eduperson_groups.union(affiliation_groups):
            if cn in groups:
                continue
            if cn not in in_cns:
                # logger.debug('already not in %s' % cn)
                continue
            if do_rems:
                logger.info('removing %s from group %s' % (netid, cn))
                ret = gws.delete_members(cn, [netid])
                # logger.info(ret)
                dels.add(cn)
            else:
                logger.info('would remove from group %s' % cn)

    except DataFailureException as e:
        logger.warn('Could not update group %s: %s' % (cn, str(e)))

    return (adds, dels)
