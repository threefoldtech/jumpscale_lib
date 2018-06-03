"""
Client factory for Rinive blockchain network, js entry point
"""

from JumpScale9 import j

from .RivineClient import RivineClient

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class OVCClientFactory(JSConfigBaseFactory):
    """
    Factroy class to get a rivine client object
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.rivine"
        self.__imports__ = "rivine"
        JSConfigBaseFactory.__init__(self, RivineClient)


    def generate_seed(self):
        """
        Generates a new seed
        """
        return j.data.encryption.mnemonic.generate(strength=256)
