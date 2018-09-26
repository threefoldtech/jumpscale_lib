"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.tfchain.TfchainClient import TfchainClient
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory,\
        DEFAULT_MINERFEE, TransactionV128, TransactionV129

JSConfigBaseFactory = j.tools.configmanager.JSBaseClassConfigs

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

    def create_transaction_from_json(self, txn_json):
        """
        Loads a transaction from a json string

        @param txn_json: Json string representing a transaction
        """
        return TransactionFactory.from_json(txn_json)

    def create_wallet (self, walletname, testnet= False, seed = ''):
        """
        Creates a named wallet

        @param seed : restores a wallet from a seed
        """
        data = {'testnet':testnet, 'seed_':seed}
        return self.get(walletname, data=data).wallet

    def open_wallet(self, walletname):
        """
        Opens a named wallet
        Returns None if the  wallet is not found
        """
        if walletname not in self.list():
            return None
        return self.get(walletname).wallet


    def create_minterdefinition_transaction(self):
        """
        Create a new minter definition transaction
        """
        tx = TransactionV128()
        tx.add_minerfee(DEFAULT_MINERFEE)
        return tx

    def create_coincreation_transaction(self):
        """
        Create a new coin creation transaction
        """
        tx = TransactionV129()
        tx.add_minerfee(DEFAULT_MINERFEE)
        return tx
