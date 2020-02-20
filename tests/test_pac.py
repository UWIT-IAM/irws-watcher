from mock import patch

from apps import pac

from resttools.irws import IRWS
from resttools.exceptions import DataFailureException

import logging.config

import mock_settings as settings
from mock_irws import IRWS
from mock_smtplib import SMTP
import data.mock_irws_data as irws_data

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('stdout')

pac.logger = logger
pac.irws = IRWS(settings.IRWS_CONF)

@patch('smtplib.SMTP', side_effect=SMTP)
def test_process_pac_as_needed_id1(object):

    # test already has netid
    ret = pac.process_pac_as_needed('regid1')
    assert not ret

    # test disusered
    ret = pac.process_pac_as_needed('regid2')
    assert not ret

    # test netid but no password
    ret = pac.process_pac_as_needed('regid3')
    assert not ret

    # test needs netid
    ret = pac.process_pac_as_needed('regid4')
    assert ret
    
