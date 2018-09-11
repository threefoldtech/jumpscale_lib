"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.tfchain.TfchainClient import TfchainClient

JSConfigBaseFactory = j.tools.configmanager.base_class_configs

class TfchainClientFactory(JSConfigBaseFactory):
    """
    Factory class to get a tfchain client object
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.tfchain"
        self.__imports__ = "tfchain"
        JSConfigBaseFactory.__init__(self, TfchainClient)

    def generate_seed(self):
        """
        Generates a new seed and returns it as a mnemonic
        """
        return j.data.encryption.mnemonic.generate(strength=256)
