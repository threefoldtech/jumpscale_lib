from .ZeroHubClient import ZeroHubClient
from js9 import j


class ZeroStorFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.zerohub"
        self.logger = j.logger.get("j.clients.zerohub")

    def getClient(self, ...):
        """
        # Getting client via accesstoken


        """
        return ZeroHubClient...)
