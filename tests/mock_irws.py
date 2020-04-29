# mock IRWS client

from six.moves.urllib.parse import quote
import data.mock_irws_data as data

from resttools.models.irws import Categories
from resttools.models.irws import UWNetId
from resttools.models.irws import Person
from resttools.models.irws import SdbPerson
from resttools.models.irws import AdvancePerson
from resttools.models.irws import SponsoredPerson
from resttools.models.irws import CascadiaPerson
from resttools.models.irws import PDSEntry
from resttools.models.irws import Subscription
from resttools.models.irws import Pac

from resttools.exceptions import DataFailureException, InvalidIRWSName
from resttools.exceptions import ResourceNotFound, BadInput

put_pacs = []


class IRWS(object):

    def __init__(self, conf):

        self._service_name = conf['SERVICE_NAME']

    def _clean(self, arg):
        if arg is not None:
            arg = quote(arg)
        return arg

    # we always use netid
    def get_person(self, netid=None, regid=None, eid=None):
        if netid is not None:
            if netid not in data.person:
                return None
            person = Person()
            person.identifiers = data.person[netid]['identifiers']
            return person
        if regid is not None:
            if regid not in data.person:
                return None
            person = Person()
            person.identifiers = data.person[regid]['identifiers']
            return person

    def get_categories(self, netid=None, regid=None):
        categories = Categories()
        categories.categories = data.person[netid]['categories']
        return categories

    def get_sdb_person(self, vid):
        sdb = SdbPerson()
        sdb.status_code = data.sdb[vid]['status_code']
        sdb.sdb_class = data.sdb[vid]['sdb_class']
        sdb.branch = data.sdb[vid]['branch']
        return sdb

    def get_advance_person(self, vid):
        advance = AdvancePerson()
        advance.status_code = data.advance[vid]['status_code']
        advance.source_code = data.advance[vid]['source_code']
        advance.alumni_member = data.advance[vid]['alumni_member']
        advance.alumni_type = data.advance[vid]['alumni_type']
        return advance

    def get_sponsored_person(self, source, id):
        if id not in data.sponsored:
            return None
        sponsored = SponsoredPerson()
        sponsored.status_code = data.sponsored[id]['status_code']
        sponsored.pac = data.sponsored[id]['pac']
        sponsored.fname = data.sponsored[id]['fname']
        sponsored.lname = data.sponsored[id]['lname']
        sponsored.contact_email = data.sponsored[id]['contact_email']
        return sponsored

    def get_pdsentry_by_netid(self, netid):
        pds = PDSEntry()
        pds.edupersonaffiliation = data.pds[netid]['edupersonaffiliation']
        return pds

    # we only use regid
    def get_uwnetid(self, regid=None, netid=None, status=None):
        regid = self._clean(regid)
        netid = self._clean(netid)

        if regid is not None:
            if regid not in data.uwnetid:
                return None
            uwnetid = UWNetId()
            uwnetid.uwnetid = data.uwnetid[regid]['uwnetid']
            uwnetid.disenfran = data.uwnetid[regid]['disenfran']
            return uwnetid
        return None

    def get_subscription(self, netid, subscription):
        netid = self._clean(netid)
        if netid is not None:
            if netid not in data.subscription or data.subscription[netid]['subscription'] != 60:
                return None
            sub = Subscription()
            sub.uwnetid = data.subscription[netid]['uwnetid']
            return sub
        return None

    def put_pac(self, id, source=None):
        id = self._clean(id)
        source = self._clean(source)
        if id not in data.pac:
            return None
        pac = Pac
        pac.pac = data.pac[id]['pac']
        pac.expiration = data.pac[id]['expiration']
        put_pacs.append(pac.pac)
        return pac
