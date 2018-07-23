"""
Client factory for electrum wallet
"""

from JumpScale9 import j

from .ElectrumClient import ElectrumClient

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class ElectrumClientFactory(JSConfigBaseFactory):
    """
    Factroy class to get a electrum client object
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.electrum"
        # self.__imports__ = "electrum"
        JSConfigBaseFactory.__init__(self, ElectrumClient)
