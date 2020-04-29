# mock IRWS client

import data.mock_gws_data as data

from resttools.exceptions import DataFailureException, InvalidIRWSName
from resttools.exceptions import ResourceNotFound, BadInput


class GWS(object):

    def __init__(self, conf):
        self._puts = set()

    def is_direct_member(self, cn, netid):
        return cn in data.member[netid]

    def put_members(self, cn, members):
        for member in members:
            self._puts.add((cn, member))

    def number_puts():
        return len(self._puts)

    def was_put(cn, member):
        return (cn, member) in self._puts
