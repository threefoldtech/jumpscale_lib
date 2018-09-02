from jumpscale import j

JSConfigFactory = j.tools.configmanager.base_class_configs

from .BTCClient import BTCClient

class GitHubFactory(JSConfigFactory):

    __jslocation__ = "j.clients.btc_alpha"
    def __init__(self):
        JSConfigFactory.__init__(self, BTCClient)
