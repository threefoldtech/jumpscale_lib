from .ZeroHubClient import ZeroHubClient
from js9 import j

class ZeroHubFactory:
    def __init__(self):
        self.__jslocation__ = "j.clients.zerohub"
        self.logger = j.logger.get("j.clients.zerohub")

    def getClient(self, token=None):
        """
        # Getting client via accesstoken

        """
        cl = ZeroHubClient()

        if token:
            cl.api.set_token(token)

        return cl
