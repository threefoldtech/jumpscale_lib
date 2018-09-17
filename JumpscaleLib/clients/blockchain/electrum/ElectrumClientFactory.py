"""
Client factory for electrum wallet
"""

from Jumpscale import j

from electrum.commands import Commands
from .ElectrumClient import ElectrumClient

JSConfigBaseFactory = j.tools.configmanager.JSBaseClassConfigs


class ElectrumClientFactory(JSConfigBaseFactory):
    """
    Factroy class to get a electrum client object
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.btc_electrum"
        # self.__imports__ = "electrum"
        JSConfigBaseFactory.__init__(self, ElectrumClient)


    def generate_seed(self, nbits=132):
        """
        Creates a new seed

        @param nbits: Number of bits for creating the seed default is 132 which will generate a 12 words seed
        """
        cmd = Commands(None, None, None)
        return cmd.make_seed(nbits=nbits)
