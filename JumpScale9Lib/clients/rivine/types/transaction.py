"""
Module contianing all transaction types
"""
from JumpScale9Lib.clients.rivine.types.signatures import Ed25519PublicKey
from JumpScale9Lib.clients.rivine.types.unlockconditions import SingleSignatureFulfillment, UnlockHashCondition

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
        self._coins_inputs = []
        self._blockstakes_inputs = []
        self._coins_outputs = []
        self._blockstakes_outputs = []
        self._minerfees = []
        self._data = bytearray()


    @property
    def coins_inputs(self):
        """
        Retrieves coins inputs
        """
        return self._coins_inputs

    @property
    def coins_outputs(self):
        """
        Retrieves coins outputs
        """
        return self._coins_outputs


    def add_data(self, data):
        """
        Add data to the transaction
        """
        self._data.extend(data)


    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coins_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


    def add_coin_output(self, value, recipient):
        """
        Add a new coin output to the transaction

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        self._coins_outputs.append(CoinOutput(value=value, condition=UnlockHashCondition(unlockhash=recipient)))


    def add_minerfee(self, minerfee):
        """
        Adds a minerfee to the transaction
        """
        self._minerfees.append(minerfee)


    def get_input_signature_hash(self, input_index):
        """
        Builds a signature hash for an input
        """
        




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

    @property
    def parent_id(self):
        return self._parent_id


class CoinOutput:
    """
    CoinOutput calss
    """
    def __init__(self, value, condition):
        """
        Initializes a new coinoutput
        """
        self._value = value
        self._condition = condition
