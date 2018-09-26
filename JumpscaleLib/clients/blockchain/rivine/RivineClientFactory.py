"""
Client factory for Rinive blockchain network, js entry point
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.rivine.RivineClient import RivineClient
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory,\
        DEFAULT_MINERFEE, TransactionV128

JSConfigBaseFactory = j.tools.configmanager.JSBaseClassConfigs


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


    def create_minterdefinition_transaction(self):
        """
        Create a new minter definition transaction
        """
        tx = TransactionV128()
        tx.add_minerfee(DEFAULT_MINERFEE)
        return tx
