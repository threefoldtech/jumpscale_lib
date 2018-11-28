from .BTCClient import BTCClient
from jumpscale import j

JSConfigFactory = j.tools.configmanager.base_class_configs


class GitHubFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.btc_alpha"
        JSConfigFactory.__init__(self, BTCClient)
