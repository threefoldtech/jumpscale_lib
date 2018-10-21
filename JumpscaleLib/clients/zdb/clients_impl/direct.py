from ..ZDBClientBase import ZDBClientBase


class ZDBClientDirectMode(ZDBClientBase):

    def __init__(self, nsname, addr="localhost", port=9900, secret="123456", admin_secret=None):
        super().__init__(addr=addr, port=port, mode="direct", nsname=nsname, ns_secret=secret, admin_secret=admin_secret)

    # No custom logic yet
