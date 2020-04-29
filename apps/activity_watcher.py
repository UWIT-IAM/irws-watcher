#  ========================================================================
#  Copyright (c) 2020 The University of Washington
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  ========================================================================
#

#
# Handle identity messages (irws) relating to groups and affiliations and etc.
#

import base64
import string
import time
import re
import sys
import json
import argparse
import jinja2

import logging.config

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser

from messagetools.iam_message import crypt_init
from messagetools.aws import AWS
from resttools.irws import IRWS
from resttools.gws import GWS
from resttools.exceptions import DataFailureException

import pac
import affiliation

# clients
irws_client = None
gws_client = None
aws_client = None

# action activation flags
doing_adds = False
doing_rems = False
doing_pacs = False

#
# Process a message
# returns True unless recoverable error
#


def process_message(message):

    global doing_adds
    global doing_rems
    global doing_pacs

    hdr = message[u'header']
    # print('message received: type: %s' % (hdr[u'messageType']))
    # print('uuid: ' + hdr[u'messageId'])
    # print('sent: ' + hdr[u'timestamp'])
    # print('sender: ' + hdr[u'sender'])
    # print('contentType: ' + hdr[u'contentType'])
    # logger.debug('context: [%s]' % hdr[u'messageContext'])
    # logger.debug('message: [%s]' % message[u'body'])

    # verify correct system type ?

    ret = True
    if hdr[u'sender'] == 'idregistry':
        try:
            context = json.loads(hdr[u'messageContext'])
        except ValueError:
            logger.info('bad json')
            logger.info(hdr[u'messageContext'])
            return True
        body = json.loads(message[u'body'])

        if context[u'topic'] == 'source':
            logger.debug('msg: topic=source, source=' + body[u'source'])
        else:
            logger.debug('msg: topic=' + context[u'topic'])

        # source events
        if context[u'topic'] == 'source' and (body[u'type'] == 'insert' or body[u'type'] == 'modify') and body[u'source'] == '6':
            logger.debug('src6 id=' + body[u'id'])
            sent = pac.process_pac_as_needed(body[u'regid'], body[u'id'], do_pacs=doing_pacs)

        # uwnetid events = netid affiliation changes
        elif context[u'topic'] == 'uwnetid':
            if u'uwnetid' in body:
                (adds, dels) = affiliation.process_affiliations_as_needed(body['uwnetid'], do_adds=doing_adds, do_rems=doing_rems)

    return ret


#
# ---------- main -------------------
#

# configure

parser = argparse.ArgumentParser('Monitor irws source and netid topics')
parser.add_argument('-s', '--settings', action='store', dest='settings', help='?')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='?')
parser.add_argument('-m', '--max_messages', action='store', type=int, dest='maxmsg', help='maximum messages to process.', default=0)
parser.add_argument('-l', '--logname', action='store', dest='logname', help='process logname.', default='activity')
parser.add_argument('-c', '--count', action='store_true', dest='count_only', help='just count the messages on the queue', default=False)
parser.add_argument('--add-members', action='store_true', dest='do_adds', help='Add members to groups as needed')
parser.add_argument('--remove-members', action='store_true', dest='do_rems', help='Remove members from groups as needed')
parser.add_argument('--send-pacs', action='store_true', dest='do_pacs', help='Send pacs as needed')
args = parser.parse_args()


logname = 'activity'
if args.verbose:
    logname = 'activity-verbose'

settingpy = 'settings'
if args.settings is not None:
    settingpy = args.settings
settings = __import__(settingpy)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(logname)
logger.info("IRWS activity watcher starting:  %s" % settings.SETTINGS_NAME)

max_messages = 0
if args.maxmsg > 0:
    max_messages = args.maxmsg
nmpc = 10 if max_messages == 0 else max_messages

audit_logger = logging.getLogger('audit')

# setup template engine for emails ( note path in settings )
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)

idle1 = 0  # 1 minute counter
idle5 = 0  # 5 minute counter

nmsg = 0

if args.count_only:
    aws_client = AWS(settings.AWS_CONF)
    q = aws_client.get_queue()
    print('queue has %d messages' % q.count())
    sys.exit()


irws_client = IRWS(settings.IRWS_CONF)
aws_client = AWS(settings.AWS_CONF)
gws_client = GWS(settings.GWS_CONF)
crypt_init(settings.IAM_CONF)

pac.logger = logger
pac.irws = irws_client
pac.conf = settings.PAC_CONF

affiliation.logger = logger
affiliation.irws = irws_client
affiliation.gws = gws_client
affiliation.parse_filter_file(settings.FILTER_FILE)

doing_adds = args.do_adds
doing_rems = args.do_rems
doing_pacs = args.do_pacs
if not doing_adds:
    logger.info('Member add is disable. Use "--add-members" to activate.')
if not doing_rems:
    logger.info('Member removal is disable. Use "--remove-members" to activate.')
if not doing_pacs:
    logger.info('PAC updates and emails are disable. Use "--send-pacs" to activate.')


while max_messages == 0 or nmsg < max_messages:

    # message = aws_client.recv_message()
    # if message == None:
    nt, ng = aws_client.recv_and_process(process_message, nmpc)
    if ng == 0:
        sleep_sec = settings.LONG_SLEEP
        if idle5 == 0:
            idle1 += 1
            if idle1 >= 30:
                idle5 = 1
            sleep_sec = settings.SHORT_SLEEP
        # logger.debug('sleep %d seconds' % (sleep_sec))
        time.sleep(sleep_sec)
        continue
    else:
        nmsg += ng
        idle1 = 0
        idle5 = 0

num_processed = 0
