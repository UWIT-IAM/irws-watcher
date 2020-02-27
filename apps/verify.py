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
# verify a netid's affiliations
#

import base64
import string
import time
import re
import sys
import json
import argparse

import logging.config

from messagetools.iam_message import crypt_init
from messagetools.aws import AWS
from resttools.irws import IRWS
from resttools.gws import GWS
from resttools.exceptions import DataFailureException

import affiliation
import pac

# clients
irws_client = None
gws_client = None

#
# ---------- main -------------------
#

# configure

parser = argparse.ArgumentParser('Verify netid affiliations or PAC needs.')
parser.add_argument('-s', '--settings', action='store', dest='settings', help='?')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='?')
parser.add_argument('-n', '--netid', action='store', dest='netid', help='NetId to verify (affiliations)')
parser.add_argument('-r', '--regid', action='store', dest='regid', help='Regid to verify (send pac)')

args = parser.parse_args()

logname = 'verify'

settingpy = 'settings'
if args.settings is not None:
    settingpy = args.settings
settings = __import__(settingpy)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(logname)
logger.info("IRWS verify watcher starting:  %s" % settings.SETTINGS_NAME)

irws_client = IRWS(settings.IRWS_CONF)
gws_client = GWS(settings.GWS_CONF)

affiliation.logger = logger
affiliation.irws = irws_client
affiliation.gws = gws_client
affiliation.parse_filter_file(settings.FILTER_FILE)
pac.logger = logger
pac.irws = irws_client
pac.conf = settings.PAC_CONF

if args.netid is not None:
    affiliation.process_affiliations_as_needed(args.netid)
elif args.regid is not None:
    pac.process_pac_as_needed(args.regid)
else:
    print("A netid or regid is required")
