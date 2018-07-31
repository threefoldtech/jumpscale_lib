"""
This module implements a light weight wallet for Rivine blockchain network.
the wallet will need the following functionality:

- Starting from a seed, be able to derive the public and private keypairs.
- Use the public keys to create unlockcondition objects, which can be hashed to get the addresses.
- These addresses can be used to query the explorer to get the coininputs
- Remove those that are already spent
- When creating the transaction, select the coin inputs to have equal or more coins than the required output + minerfee. Change can be written back to one of your own addresses. Note that an input must be consumed in its entirety.
- For every public key in the input, the corresponding private key is required to sign the transaction to be valid
"""

import ed25519
from pyblake2 import blake2b
from functools import partial
import requests
import base64
import time
from .encoding import binary
from .types.signatures import Ed25519PublicKey, SPECIFIER_SIZE
from .types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY, UNLOCKHASH_SIZE, UNLOCKHASH_CHECKSUM_SIZE

from JumpScale9 import j
from JumpScale9Lib.clients.blockchain.rivine import utils
from JumpScale9Lib.clients.blockchain.rivine.atomicswap.atomicswap import AtomicSwapManager
from JumpScale9Lib.clients.blockchain.rivine.types.transaction import TransactionFactory, DEFAULT_TRANSACTION_VERSION
from JumpScale9Lib.clients.blockchain.rivine.types.unlockhash import UnlockHash

from .const import MINER_PAYOUT_MATURITY_WINDOW, WALLET_ADDRESS_TYPE, ADDRESS_TYPE_SIZE, HASTINGS_TFT_VALUE, UNLOCKHASH_TYPE

from .errors import RESTAPIError, BackendError,\
InsufficientWalletFundsError, NonExistingOutputError,\
NotEnoughSignaturesFound, InvalidUnlockHashChecksumError

logger = j.logger.get(__name__)

class RivineWallet:
    """
    Wallet class
    """
    def __init__(self, seed, bc_network, bc_network_password, nr_keys_per_seed=50, minerfee=100000000, client=None):
        """
        Creates new wallet
        TODO: check if we need to support multiple seeds from the begining

        @param seed: Starting point seed to generate keys.
        @param bc_network: Blockchain network to use.
        @param bc_network_password: Password to send to the explorer node when posting requests.
        @param nr_keys_per_seed: Number of keys generated from the seed.
        @param minerfee: Amount of hastings that should be minerfee (default to 0.1 TFT)
        @param client: Name of the insance of the j.clients.rivine that is used to create the wallet
        """
        self._client = j.clients.rivine.get(client) if client else None
        self._seed = j.data.encryption.mnemonic.to_entropy(seed)
        self._unspent_coins_outputs = {}
        self._keys = {}
        self._bc_network = bc_network.strip("/")
        self._minerfee = minerfee
        self._bc_network_password = bc_network_password
        self._nr_keys_per_seed = nr_keys_per_seed
        for index in range(self._nr_keys_per_seed):
            key = self._generate_spendable_key(index=index)
            self._keys[str(key.unlockhash)] = key
        self._addresses_info = {}
        self.atomicswap = AtomicSwapManager(wallet=self)


    @property
    def addresses(self):
        """
        Wallet addresses to recieve and send funds
        """
        return [str(key) for key in self._keys.keys()]


    @property
    def current_balance(self):
        """
        Retrieves current wallet balance
        """
        self._check_balance()
        return sum(int(value.get('value', 0)) for value in self._unspent_coins_outputs.values()) / HASTINGS_TFT_VALUE


    def generate_address(self):
        """
        Generates a new wallet address
        """
        key = self._generate_spendable_key(index=self._nr_keys_per_seed)
        address = str(key.unlockhash)
        self._keys[address] = key
        self._nr_keys_per_seed += 1
        if self._client is not None:
            # we need to update the config with the new nr_of_keys_per_seed for this wallet
            data = dict(self._client.config.data)
            data['nr_keys_per_seed'] = self._nr_keys_per_seed
            cl = j.clients.rivine.get(instance=self._client.instance,
                                       data=data,
                                       create=True,
                                       interactive=False)
            cl.config.save()

        return address


    def _generate_spendable_key(self, index):
        """
        Generate a @Spendablekey object from the seed and index

        @param index: Index of key to generate from the seed
        """
        binary_seed = bytearray()
        binary_seed.extend(binary.encode(self._seed))
        binary_seed.extend(binary.encode(index))
        binary_seed_hash = utils.hash(binary_seed)
        sk = ed25519.SigningKey(binary_seed_hash)
        pk = sk.get_verifying_key()
        return SpendableKey(pub_key=pk.to_bytes(), sec_key=sk)


    def _get_current_chain_height(self):
        """
        Retrieves the current chain height
        """
        return utils.get_current_chain_height(self._bc_network)


    def _check_address(self, address, log_errors=True):
        """
        Check if an address is valid
        performs a http call to an explorer to check if an address has (an) (unspent) output(s)

        @param address: Address to check
        @param log_errors: If False, no logging will be executed

        @raises: @RESTAPIError if failed to check address
        """
        return utils.check_address(self._bc_network, address, log_errors)


    def _check_balance(self):
        """
        Syncs the wallet with the blockchain

        @TOCHECK: this needs to be synchronized with locks or other primitive
        """
        current_chain_height = self._get_current_chain_height()
        unconfirmed_txs = self._get_unconfirmed_transactions(format_inputs=True)
        logger.info('Current chain height is: {}'.format(current_chain_height))
        for address in self.addresses:
            try:
                address_info = self._check_address(address=address, log_errors=False)
            except RESTAPIError:
                pass
            else:
                if address_info.get('hashtype', None) != UNLOCKHASH_TYPE:
                    raise BackendError('Address is not recognized as an unblock hash')
                self._addresses_info[address] = address_info
                self._collect_miner_fees(address=address, blocks=address_info.get('blocks',{}),
                                        height=current_chain_height)
                transactions = address_info.get('transactions', {})
                self._collect_transaction_outputs(current_height=current_chain_height,
                                                  address=address,
                                                  transactions=transactions,
                                                  unconfirmed_txs=unconfirmed_txs)
        # remove spent inputs after collection all the inputs
        for address, address_info in self._addresses_info.items():
            self._remove_spent_inputs(transactions = address_info.get('transactions', {}))


    def _collect_miner_fees(self, address, blocks, height):
        """
        Scan the bocks for miner fees and Collects the miner fees But only that have matured already

        @param address: address to collect miner fees for
        @param blocks: Blocks from an address
        @param height: The current chain height
        """
        self._unspent_coins_outputs.update(utils.collect_miner_fees(address, blocks, height))


    def _collect_transaction_outputs(self, current_height, address, transactions, unconfirmed_txs=None):
        """
        Collects transactions outputs

        @param current_height: Current chain height
        @param address: address to collect transactions outputs
        @param transactions: Details about the transactions
        @param unconfirmed_txs: List of unconfirmed transactions
        """
        unlocked_txn_outputs = utils.collect_transaction_outputs(current_height, address, transactions, unconfirmed_txs)['unlocked']
        self._unspent_coins_outputs.update(unlocked_txn_outputs)


    def _remove_spent_inputs(self, transactions):
        """
        Remvoes the already spent outputs

        @param transactions: Details about the transactions
        """
        utils.remove_spent_inputs(self._unspent_coins_outputs, transactions)


    def _get_unconfirmed_transactions(self, format_inputs=False):
        """
        Retrieves the unconfirmed transaction from a remote node that runs the Transaction pool module

        @param format_inputs: If True, the output will be formated to get a list of the inputs parent ids

        # example output
                {'transactions': [{'version': 1,
           'data': {'coininputs': [{'parentid': '7616c88f452d6b22a3683bcbdfdf6ee3c32b63a810a8ac0d46a7403a33d4c06f',
              'fulfillment': {'type': 1,
               'data': {'publickey': 'ed25519:9413b12a6158f52fad6c39cc164054a9e7fbe5378892311f498eae56f80c068a',
                'signature': '34cee9bbc380deba2f52ccb20c2a47d4f6001fe66cfe7079d6b71367ea14544e89e69657201d0cc7b7b901324e64a7f4dce6ac6177536726cee576a0b74a8700'}}}],
            'coinoutputs': [{'value': '2000000000',
              'condition': {'type': 1,
               'data': {'unlockhash': '0112a7c1813746c5f6d5d496441d7a6a226984a3cc318021ee82b5695e4470f160c6ca61f66df2'}}},
             {'value': '3600000000',
              'condition': {'type': 1,
               'data': {'unlockhash': '012bdb563a4b3b630ddf32f1fde8d97466376a67c0bc9a278c2fa8c8bd760d4dcb4b9564cdea6f'}}}],
            'minerfees': ['100000000']}}]}
        """
        return utils.get_unconfirmed_transactions(self._bc_network, format_inputs=format_inputs)


    def send_money(self, amount, recipient, data=None, locktime=None):
        """
        Sends TFT tokens from the user's wallet to the recipient address

        @param amount: Amount to be transfered in TF tokens
        @param recipient: Address of the fund recipient
        @param data: Custom data to be sent with the transaction
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        if data is not None:
            data = binary.encode(data)
        # convert amount to hastings
        amount = int(amount * HASTINGS_TFT_VALUE)
        transaction = self._create_transaction(amount=amount,
                                                recipient=recipient,
                                                sign_transaction=True,
                                                custom_data=data,
                                                locktime=locktime)
        self._commit_transaction(transaction=transaction)
        return transaction


    def send_to_many(self, amount, recipients, required_nr_of_signatures, data=None, locktime=None):
        """
        Sends funds to multiple recipients
        Also specificies how many recipients need to sign before the funds can be spent

        @param amount: The amount needed to be transfered in TF Tokens
        @param recipients: List of recipients addresses.
        @param required_nr_of_signatures: Defines the amount of signatures required in order to spend this fund.
        @param data: Custom data to add to the transaction record
        @type custom_data: bytearray
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """

        if data is not None:
            data = binary.encode(data)
        # convert amount to hastings
        amount = int(amount * HASTINGS_TFT_VALUE)
        transaction = self._create_multisig_transaction(amount=amount,
                                                        recipients=recipients,
                                                        min_nr_sig=required_nr_of_signatures,
                                                        sign_transaction=True,
                                                        custom_data=data,
                                                        locktime=locktime)
        self._commit_transaction(transaction=transaction)
        return transaction


    def _get_inputs(self, amount, minerfee=None):
        """
        Retrieves the inputs data that can cover the specified amount

        @param amount: The amount of funds that needs to be covered

        @returns: a tuple of (input info dictionary, the used addresses, minerfee, remainder)
        """
        if minerfee is None:
            minerfee = self._minerfee
        wallet_fund = int(self.current_balance * HASTINGS_TFT_VALUE)
        required_funds = amount + minerfee
        if required_funds > wallet_fund:
            raise InsufficientWalletFundsError('No sufficient funds to make the transaction')

        result = []
        input_value = 0
        used_addresses = {}
        for address, unspent_coin_output in self._unspent_coins_outputs.items():
            # if we reach the required funds, then break
            if input_value >= required_funds:
                break
            input_result = {}
            ulh = self._get_unlockhash_from_output(output=unspent_coin_output, address=address)

            if not ulh:
                raise RuntimeError('Cannot retrieve unlockhash')

            # used_addresses.append(ulh)
            used_addresses[address] = ulh
            input_result['parent_id'] = address
            input_result['pub_key'] = self._keys[ulh].public_key

            input_value += int(unspent_coin_output['value'])
            result.append(input_result)
        return result, used_addresses, minerfee, (input_value - required_funds)


    def _create_multisig_transaction(self, amount, recipients, min_nr_sig=None, minerfee=None, sign_transaction=True, custom_data=None, locktime=None):
        """
        Creates a transaction with Mulitsignature condition
        MultiSignature Condition allows the funds to be sent to multiple wallet addresses and specify how many signatures required to make this transaction spendable

        @param amount: The amount needed to be transfered in hastings
        @param recipients: List of recipients addresses.
        @param min_nr_sig: Defines the amount of signatures required in order to spend this output
        @param minerfee: The minerfee for this transaction in hastings
        @param sign_transaction: If True, the created transaction will be singed
        @param custom_data: Custom data to add to the transaction record
        @type custom_data: bytearray
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)

        # set the the custom data on the transaction
        if custom_data is not None:
            transaction.add_data(custom_data)


        input_results, used_addresses, minerfee, remainder = self._get_inputs(amount=amount)
        for input_result in input_results:
            transaction.add_coin_input(**input_result)

        for txn_input in transaction.coins_inputs:
            if used_addresses[txn_input.parent_id] not in self._keys:
            # if self._unspent_coins_outputs[txn_input.parent_id][ulh] not in self._keys:
                raise NonExistingOutputError('Trying to spend unexisting output')

        transaction.add_multisig_output(value=amount, unlockhashes=recipients, min_nr_sig=min_nr_sig, locktime=locktime)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            for address in self._keys.keys():
                if address in used_addresses.values():
                    continue
                transaction.add_coin_output(value=remainder, recipient=address)
                break

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        if sign_transaction:
            # sign the transaction
            self._sign_transaction(transaction)

        return transaction


    def _create_transaction(self, amount, recipient, minerfee=None, sign_transaction=True, custom_data=None, locktime=None):
        """
        Creates new transaction and sign it
        creates a new transaction of the specified ammount to a specified address. A remainder address
        to which the leftover coins will be transfered (if any) is chosen automatically. An error is returned if the coins
        available in the coininputs are insufficient to cover the amount specified for transfer (+ the miner fee).

        @param amount: The amount needed to be transfered in hastings
        @param recipient: Address of the recipient.
        @param minerfee: The minerfee for this transaction in hastings
        @param sign_transaction: If True, the created transaction will be singed
        @param custom_data: Custom data to add to the transaction record
        @type custom_data: bytearray
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)

        # set the the custom data on the transaction
        if custom_data is not None:
            transaction.add_data(custom_data)


        input_results, used_addresses, minerfee, remainder = self._get_inputs(amount=amount)
        for input_result in input_results:
            transaction.add_coin_input(**input_result)

        for txn_input in transaction.coins_inputs:
            if used_addresses[txn_input.parent_id] not in self._keys:
            # if self._unspent_coins_outputs[txn_input.parent_id][ulh] not in self._keys:
                raise NonExistingOutputError('Trying to spend unexisting output')

        transaction.add_coin_output(value=amount, recipient=recipient, locktime=locktime)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            for address in self._keys.keys():
                if address in used_addresses.values():
                    continue
                transaction.add_coin_output(value=remainder, recipient=address)
                break

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        if sign_transaction:
            # sign the transaction
            self._sign_transaction(transaction)

        return transaction


    def _get_unlockhash_from_output(self, output, address):
        """
        Retrieves unlockhash from coin output. This should handle different types of output conditions and transaction formats
        """
        ulh = utils.get_unlockhash_from_output(output, address, current_height=self._get_current_chain_height())
        return ulh['unlocked'][0] if ulh['unlocked'] else None


    def _sign_transaction(self, transaction):
        """
        Signs a transaction with the existing keys.

        @param transaction: Transaction object to be signed
        """
        logger.info("Signing Trasnaction")
        for index, input in enumerate(transaction.coins_inputs):
            #@TODO improve the parsing of outputs its duplicated now in too many places
            ulh = self._get_unlockhash_from_output(output=self._unspent_coins_outputs[input.parent_id], address=input.parent_id)
            if ulh is not None:
                key = self._keys[ulh]
                input.sign(input_idx=index, transaction=transaction, secret_key=key.secret_key)
            else:
                logger.warn("Failed to retrieve unlockhash related to input {}".format(input))


    def _commit_transaction(self, transaction):
        """
        Commits a singed transaction to the chain

        @param transaction: Transaction object to be committed
        """
        return utils.commit_transaction(self._bc_network, self._bc_network_password, transaction)


    def sign_transaction(self, transaction, multisig=False, commit=False):
        """
        Signs a transaction and optionally push it to the blockchain

        @param transaction: Transaction object
        @param multisig: If True, it indicates that the transaction contains multisig inputs
        @param commit: If True, the transaction will be pushed to the chain after being signed
        """
        if not multisig:
            self._sign_transaction(transaction=transaction)
        else:
            current_height = self._get_current_chain_height()
            for index, ci in enumerate(transaction.coins_inputs):
                output_info = self._check_address(ci._parent_id)
                for txn_info in output_info['transactions']:
                    for co in txn_info['rawtransaction']['data']['coinoutputs']:
                        ulhs = utils.get_unlockhash_from_output(output=co,
                                                                address=ci._parent_id,
                                                                current_height=current_height)
                        ulh = list(set(self.addresses).intersection(ulhs['unlocked']))
                        if ulh:
                            ulh = ulh[0]
                            key = self._keys[ulh]
                            ci.sign(input_idx=index, transaction=transaction, secret_key=key.secret_key)
                        else:
                            logger.warn("Failed to retrieve unlockhash related to input {}".format(ci._parent_id))

        if commit:
            self._commit_transaction(transaction=transaction)

        return transaction


class SpendableKey:
    """
    SpendableKey is a secret signing key and its public verifying key
    """

    def __init__(self, pub_key, sec_key):
        """
        Creates new SpendableKey

        @param pub_key: A 32-bytes verifying key
        @param sec_key: A signing key that correspond to the verifying key
        """
        self._sk = sec_key
        self._pk = pub_key
        self._unlockhash = None


    @property
    def public_key(self):
        """
        Return the public verification key
        """
        return self._pk

    @property
    def secret_key(self):
        """
        Returns the secret key
        """
        return self._sk



    @property
    def unlockhash(self):
        """
        Calculate unlock hash of the spendable key
        """
        if self._unlockhash is None:
            pub_key = Ed25519PublicKey(pub_key=self._pk)
            encoded_pub_key = binary.encode(pub_key)
            hash = utils.hash(encoded_pub_key, encoding_type='slice')
            self._unlockhash = UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
        return self._unlockhash
