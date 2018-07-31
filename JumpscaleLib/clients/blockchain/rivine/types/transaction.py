"""
Module contianing all transaction types
"""
from JumpScale9Lib.clients.blockchain.rivine.types.signatures import Ed25519PublicKey
from JumpScale9Lib.clients.blockchain.rivine.types.unlockconditions import SingleSignatureFulfillment, UnlockHashCondition,\
 LockTimeCondition, AtomicSwapCondition, AtomicSwapFulfillment, MultiSignatureCondition, FulfillmentFactory, UnlockCondtionFactory, MultiSignatureFulfillment
from JumpScale9Lib.clients.blockchain.rivine.encoding import binary
from JumpScale9Lib.clients.blockchain.rivine.utils import hash
from JumpScale9Lib.clients.blockchain.rivine.types.unlockhash import UnlockHash

import base64
import json

DEFAULT_TRANSACTION_VERSION = 1
HASHTYPE_COINOUTPUT_ID = 'coinoutputid'

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


    @staticmethod
    def from_json(txn_json):
        """
        Creates a new transaction object from a json formated string

        @param txn_json: JSON string, representing a transaction
        """
        txn_dict = json.loads(txn_json)
        txn = None
        if 'version' in txn_dict:
            if txn_dict['version'] == DEFAULT_TRANSACTION_VERSION:
                txn = TransactionV1()
                if 'data' in txn_dict:
                    txn_data = txn_dict['data']
                    if 'coininputs' in txn_data:
                        for ci_info in txn_data['coininputs']:
                            ci = CoinInput.from_dict(ci_info)
                            txn._coins_inputs.append(ci)
                    if 'coinoutputs' in txn_data:
                        for co_info in txn_data['coinoutputs']:
                            co = CoinOutput.from_dict(co_info)
                            txn._coins_outputs.append(co)
                    if 'minerfees' in txn_data:
                        for minerfee in txn_data['minerfees'] :
                            txn.add_minerfee(int(minerfee))
        return txn



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
        self._version = bytearray([1])
        self._id = None


    @property
    def id(self):
        """
        Gets transaction id
        """
        return self._id

    @id.setter
    def id(self, txn_id):
        """
        Sets transaction id
        """
        self._id = txn_id

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


    @property
    def json(self):
        """
        Returns a json version of the TransactionV1 object
        """
        result = {
            'version': binary.decode(self._version, type_=int),
            'data': {
                'coininputs': [input.json for input in self._coins_inputs],
                'coinoutputs': [output.json for output in self._coins_outputs],
                'minerfees': [str(fee) for fee in self._minerfees]
            }
        }
        if self._data:
            result['data']['arbitrarydata'] = base64.b64encode(self._data).decode('utf-8')
        return result



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


    def add_atomicswap_input(self, parent_id, pub_key, secret=None):
        """
        Adds a new atomicswap input to the transaction
        An atomicswap input can be for refund or redeem purposes, if for refund no secret is needed, but if for redeem then
        a secret needs tp be provided
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = AtomicSwapFulfillment(pub_key=key, secret=secret)
        self._coins_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


    def add_multisig_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coins_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))



    def add_coin_output(self, value, recipient, locktime=None):
        """
        Add a new coin output to the transaction

        @param value: Amout of coins
        @param recipient: The recipient address
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._coins_outputs.append(CoinOutput(value=value, condition=condition))



    def add_atomicswap_output(self, value, recipient, locktime, refund_address, hashed_secret):
        """
        Add a new atomicswap output to the transaction
        """
        condition = AtomicSwapCondition(sender=refund_address, reciever=recipient,
                                        hashed_secret=hashed_secret, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coins_outputs.append(coin_output)
        return coin_output


    def add_multisig_output(self, value, unlockhashes, min_nr_sig, locktime=None):
        """
        Add a new MultiSignature output to the transaction

        @param value: Value of the output in hastings
        @param unlockhashes: List of all unlock hashes which are authorised to spend this output by signing off
        @param min_nr_sig: Defines the amount of signatures required in order to spend this output
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes,
                                            min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coins_outputs.append(coin_output)
        return coin_output


    def add_minerfee(self, minerfee):
        """
        Adds a minerfee to the transaction
        """
        self._minerfees.append(minerfee)


    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []

        buffer = bytearray()
        # encode the transaction version
        buffer.extend(self._version)
        # encode the input index
        buffer.extend(binary.encode(input_index))

        # encode extra objects if exists
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))

        # encode the number of coins inputs
        buffer.extend(binary.encode(len(self._coins_inputs)))

        # encode inputs parent_ids
        for coin_input in self._coins_inputs:
            buffer.extend(binary.encode(coin_input.parent_id, type_='hex'))

        # encode coin outputs
        buffer.extend(binary.encode(self._coins_outputs, type_='slice'))

        # encode the number of blockstakes
        buffer.extend(binary.encode(len(self._blockstakes_inputs)))
        # encode blockstack inputs parent_ids
        for bs_input in self._blockstakes_inputs:
            buffer.extend(binary.encode(bs_input.parent_id, type_='hex'))

        # encode blockstake outputs
        buffer.extend(binary.encode(self._blockstakes_outputs, type_='slice'))

        # encode miner fees
        buffer.extend(binary.encode(len(self._minerfees)))
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))

        # encode custom data_
        buffer.extend(binary.encode(self._data, type_='slice'))

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)



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


    @classmethod
    def from_dict(cls, ci_info):
        """
        Creates a new CoinInput from dict

        @param ci_info: JSON dict representing a coin input
        """
        if 'fulfillment' in ci_info:
            f = FulfillmentFactory.from_dict(ci_info['fulfillment'])
            if 'parentid' in ci_info:
                return cls(parent_id=ci_info['parentid'],
                           fulfillment=f)

    @property
    def parent_id(self):
        return self._parent_id


    @property
    def json(self):
        """
        Returns a json encoded version of the Coininput
        """
        return {
            'parentid': self._parent_id,
            'fulfillment': self._fulfillment.json
        }


    def sign(self, input_idx, transaction, secret_key):
        """
        Sign the input using the secret key
        """
        sig_ctx = {
        'input_idx': input_idx,
        'transaction': transaction,
        'secret_key': secret_key
        }
        self._fulfillment.sign(sig_ctx=sig_ctx)


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


    @classmethod
    def from_dict(cls, co_info):
        """
        Creates a new CoinOutput from dict

        @param co_info: JSON dict representing a coin output
        """
        if 'condition' in co_info:
            condition = UnlockCondtionFactory.from_dict(co_info['condition'])
            if 'value' in co_info:
                return cls(value=int(co_info['value']),
                           condition=condition)


    @property
    def binary(self):
        """
        Returns a binary encoded version of the CoinOutput
        """
        result = bytearray()
        result.extend(binary.encode(self._value, type_='currency'))
        result.extend(binary.encode(self._condition))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the CointOutput
        """
        return {
            'value': str(self._value),
            'condition': self._condition.json
        }
