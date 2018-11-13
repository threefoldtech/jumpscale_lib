"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.tfchain.TfchainClient import TfchainClient
from JumpscaleLib.clients.blockchain.tfchain.TfchainNetwork import TfchainNetwork
from JumpscaleLib.clients.blockchain.tfchain.TfchainThreeBotClient import TfchainThreeBotClient
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory,\
        TransactionV128, TransactionV129
from JumpscaleLib.clients.blockchain.rivine.types.unlockconditions import UnlockHashCondition,\
        LockTimeCondition, MultiSignatureCondition, UnlockCondtionFactory
from JumpscaleLib.clients.blockchain.rivine.types.unlockhash import UnlockHash

from JumpscaleLib.clients.blockchain.rivine.errors import WalletAlreadyExistsException

JSConfigBaseFactory = j.tools.configmanager.JSBaseClassConfigs

class TfchainClientFactory(JSConfigBaseFactory):
    """
    Factory class to get a tfchain client object
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.tfchain"
        self.__imports__ = "tfchain"
        JSConfigBaseFactory.__init__(self, TfchainClient)

    @property
    def network(self):
        return TfchainNetwork

    @property
    def threebot(self):
        return TfchainThreeBotClient

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


    def create_wallet(self, walletname, network = TfchainNetwork.STANDARD, seed = '', explorers = None, password = ''):
        """
        Creates a named wallet

        @param network : defines which network to use, use j.clients.tfchain.network.TESTNET for testnet
        @param seed : restores a wallet from a seed
        """
        if not explorers:
            explorers = []
        if self.exists(walletname):
            raise WalletAlreadyExistsException(walletname)
        data = {
            'network': network.name.lower(),
            'seed_': seed,
            'explorers': explorers,
            'password': password,
        }
        return self.get(walletname, data=data).wallet

    def open_wallet(self, walletname):
        """
        Opens a named wallet
        Returns None if the  wallet is not found
        """
        if not self.exists(walletname):
            return None
        return self.get(walletname).wallet


    def create_minterdefinition_transaction(self, condition=None, description=None, network=TfchainNetwork.STANDARD):
        """
        Create a new minter definition transaction

        @param condition: Set the minter definition to this premade condition
        @param description: Add this description as arbitrary data to the transaction
        """
        tx = TransactionV128()
        tx.add_minerfee(network.minimum_minerfee())
        if condition is not None:
           tx.set_condition(condition)
        if description is not None:
            tx.add_data(description.encode('utf-8'))
        return tx

    def create_coincreation_transaction(self, amount=None, condition=None, description=None, network=TfchainNetwork.STANDARD):
        """
        Create a new coin creation transaction. If both an amount and condition are
        given, they will be used to create a first output in the transaction

        @param amount: The amount of coins to create for the condition, if given
        @param condition: A premade condition, used to create a first output
        @param description: A description which is added to the transaction as arbitrary data
        """
        tx = TransactionV129()
        tx.add_minerfee(network.minimum_minerfee())
        if amount is not None and condition is not None:
            tx.add_output(amount, condition)
        if description is not None:
            tx.add_data(description.encode('utf-8'))
        return tx

    def create_singlesig_condition(self, address, locktime=None):
        """
        Create a new single signature condition
        """
        unlockhash = UnlockHash.from_string(address)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        return condition

    def create_multisig_condition(self, unlockhashes, min_nr_sig, locktime=None):
        """
        Create a new multisig condition
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes, min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        return condition
