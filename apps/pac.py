#
# Handle PAC emails and etc as needed
#

import base64
import string
import time
import re

import jinja2

import logging.config

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser

from resttools.exceptions import DataFailureException

# these must be set by importer
logger = None
irws = None
conf = None

# process a template file with substitutions

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)

def _data_from_template(tmpl, info):
    template = templateEnv.get_template(tmpl)
    return template.render(info)


def _make_msg_headers(msg, hdrs):
    msg['Subject'] = hdrs['Subject']
    msg['From'] = hdrs['From']
    msg['To'] = ''.join(hdrs['To'])
    if 'Cc' in hdrs:
        msg['Cc'] = ''.join(hdrs['Cc'])
    if 'Bcc' in hdrs:
        msg['Bcc'] = ''.join(hdrs['Bcc'])


#
# if new user does not have a netid yet # send PAC to allow create
# returns True if pac sent
# returns False otherwise
# raises exception on error
#

def process_pac_as_needed(regid):

    # see if there is a netid record already
    try:
        netid = irws.get_uwnetid(regid=regid, status=30)
    except DataFailureException as e:
        logger.info('data failure to get_uwnetid.  Will retry.')
        netid = irws.get_uwnetid(regid=regid, status=30)
        logger.info('get_uwnetid ok.')

    if netid is not None:
        logger.debug('person %s has a netid' % regid)
        # verify not disusered
        if netid.disenfran == '1':
            logger.info('person %s is disenfranchised' % regid)
            return False
        # see if there is a password
        sub = irws.get_subscription(netid=netid.uwnetid, subscription=60)
        if sub is not None:
            logger.debug('person %s has a subscription 60' % regid)
            return False
        logger.debug('person %s has no password, sending pac' % regid)

    # get person info - need sponsored sources
    person = irws.get_person(regid=regid)
    if person is None:
        logger.info('regid %s not found in irws' % regid)
        return False
    if 'sponsored' not in person.identifiers:
        logger.info('regid %s has no sponsored source' % regid)
        return False
    spid = person.identifiers['sponsored']
    p = spid.find('/sponsored/') + 11
    sourceid = spid[p:]
    logger.debug('id=' + sourceid)
    sponsored = irws.get_sponsored_person('6', sourceid)
    if sponsored is not None:
        if sponsored.status_code != '1':
            logger.debug('sponsored not active: status=%s' % sponsored.status_code)
            return False
        
        # if pac sent recently, we're done (6a)
        # Note.  We are not sending new pac is status is 'E'
        if sponsored.pac != '':
            logger.info('PAC for %s, already active' % regid)
            return False

        if len(sponsored.contact_email) == 0:
            logger.warn('PAC for %s needed, but no contact email' % regid)
            return False

        # if conf['EMAIL_PAC'] is false and we got to this point then log and exit
        if not conf['EMAIL_PAC']:
            logger.info('PAC for %s needed, sending PACs turned off' % regid)
            return False
    
        info = {}
        recipients = []

        info['email'] = sponsored.contact_email[0]
        info['name'] = sponsored.fname + ' ' + sponsored.lname

        # create a PAC and notify user
        try:
            pac = irws.put_pac(sourceid, source='sponsored')
        except DataFailureException as e:
            if e.status == 400:
                logger.error('msg: IRWS put pac exception for %s: %s' % (sourceid, e.msg))
            return False
        info['pac'] = pac.pac
        info['pac_exp'] = re.sub(':..$', '', pac.expiration)

        msg = MIMEMultipart('alternative')
        sender = smtplib.SMTP(conf['SMTP_SERVER'])

        # send pac to user 
        hdrs = Parser().parsestr(_data_from_template(conf['EMAIL_HEADERS'], info))
        _make_msg_headers(msg, hdrs)
        t_html = MIMEText(_data_from_template(conf['EMAIL_HTML'], info), 'html')
        t_text = MIMEText(_data_from_template(conf['EMAIL_PLAIN'], info), 'plain')

        msg.attach(t_html)
        msg.attach(t_text)
        recipients.append(info['email'])

        logger.debug('sending pac: regid=%s, contact_email=%s' % (regid, info['email']))
        if len(recipients) > 0:
            sender.sendmail(hdrs['From'], recipients, msg.as_string())
        logger.info('msg: send pac: id=%s, email=%s' % (regid, info['email']))

    return True
