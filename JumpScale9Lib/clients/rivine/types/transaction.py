"""
Module contianing all transaction types
"""
from JumpScale9Lib.clients.rivine.types.signatures import Ed25519PublicKey
from JumpScale9Lib.clients.rivine.types.unlockconditions import SingleSignatureFulfillment

DEFAULT_TRANSACTION_VERSION = 1

class TransactionFactory:
    """
    A transaction factory class
    """

    @staticmethod
    def create_transaction(version):
        """
        Creates and return a transaction of the speicfied verion

        @param version: Version of the transaction
        """
        if version == 1:
            return TransactionV1()


class TransactionV1:
    """
    A Transaction is an atomic component of a block. Transactions can contain
	inputs and outputs and even arbitrar data. They can also contain signatures to prove that a given party has
	approved the transaction, or at least a particular subset of it.

	Transactions can depend on other previous transactions in the same block,
	but transactions cannot spend outputs that they create or otherwise beself-dependent.
    """
    def __init__(self):
        """
        Initializes a new tansaction
        """
        self._coins_inputes = []
        slef._blockstakes_inputs = []
        self._coins_outputs = []
        self._blockstakes_outputs = []
        self._minerfees = []
        self._data = bytearray()

    def add_data(self, data):
        """
        Add data to the transaction
        """
        self._data.extend(data)


    def add_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coins_inputes.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


class CoinInput:
    """
    CoinIput class
    """
    def __init__(self, parent_id, fulfillment):
        """
        Initializes a new coin input object
        """
        self._parent_id = parent_id
        self._fulfillment = fulfillment
