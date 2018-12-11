from time import sleep

from Jumpscale import j

from .VirtualboxClient import VirtualboxClient

JSBASE = j.application.JSBaseClass


class VirtualboxFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.clients.virtualbox"
        JSBASE.__init__(self)
        self.logger_enable()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = VirtualboxClient()
        return self._client
