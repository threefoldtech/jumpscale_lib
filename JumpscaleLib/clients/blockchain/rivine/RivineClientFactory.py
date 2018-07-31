"""
Client factory for Rinive blockchain network, js entry point
"""

from JumpScale9 import j

from JumpScale9Lib.clients.blockchain.rivine.RivineClient import RivineClient
from JumpScale9Lib.clients.blockchain.rivine.types.transaction import TransactionFactory

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class RivineClientFactory(JSConfigBaseFactory):
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


    def create_transaction_from_json(self, txn_json):
        """
        Creates a new transaction from a json string

        @param txn_json: Json string representing a transaction
        """
        return TransactionFactory.from_json(txn_json)
