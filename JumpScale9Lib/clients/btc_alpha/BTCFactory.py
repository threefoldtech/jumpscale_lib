from js9 import j

JSConfigFactory = j.tools.configmanager.base_class_configs

from .BTCClient import BTCClient

class GitHubFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.btc_alpha"
        JSConfigFactory.__init__(self, BTCClient)