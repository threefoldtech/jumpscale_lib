from .ZeroHubClient import ZeroHubClient
from js9 import j

class ZeroHubFactory:
    def __init__(self):
        self.__jslocation__ = "j.clients.zerohub"
        self.logger = j.logger.get("j.clients.zerohub")

    def getClient(self, token=None):
        """
        Getting client (with optional accesstoken)
        """
        cl = ZeroHubClient()

        if token:
            cl.authentificate(token)

        return cl
