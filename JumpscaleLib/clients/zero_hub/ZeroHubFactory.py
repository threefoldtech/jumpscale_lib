from .ZeroHubClient import ZeroHubClient
from Jumpscale import j

JSConfigFactory = j.tools.configmanager.JSBaseClassConfigs


class ZeroHubFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.zhub"
        JSConfigFactory.__init__(self, ZeroHubClient)
