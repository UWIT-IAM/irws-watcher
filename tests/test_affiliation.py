from mock import patch

from apps import affiliation

from resttools.irws import IRWS
from resttools.gws import GWS
from resttools.exceptions import DataFailureException

import logging.config

import mock_settings as settings
from mock_irws import IRWS
from mock_gws import GWS
import data.mock_gws_data as gws_data
import data.mock_irws_data as irws_data

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('stdout')

affiliation.logger = logger


def test_parse_filter_file():
    filters = affiliation.parse_filter_file(settings.FILTER_FILE)
    assert len(filters) == 34


def test_process_affiliations_as_needed_id1():
    affiliation.parse_filter_file(settings.FILTER_FILE)

    affiliation.irws = IRWS(settings.IRWS_CONF)
    affiliation.gws = GWS(settings.GWS_CONF)

    (adds, dels) = affiliation.process_affiliations_as_needed('netid1')

    for cn in adds:
        assert cn in irws_data.member['netid1']
        assert cn not in gws_data.member['netid1']
    for cn in dels:
        assert cn not in irws_data.member['netid1']
        assert cn in gws_data.member['netid1']
