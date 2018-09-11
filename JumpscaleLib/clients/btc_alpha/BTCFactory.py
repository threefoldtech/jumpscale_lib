from Jumpscale import j

JSConfigFactory = j.tools.configmanager.JSBaseClassConfigs

from .BTCClient import BTCClient

class GitHubFactory(JSConfigFactory):

    __jslocation__ = "j.clients.btc_alpha"
    def __init__(self):
        JSConfigFactory.__init__(self, BTCClient)
