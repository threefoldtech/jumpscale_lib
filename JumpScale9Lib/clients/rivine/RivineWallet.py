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
from .merkletree import Tree
from pyblake2 import blake2b
from functools import partial
import requests
import base64
import time
from requests.auth import HTTPBasicAuth
from .encoding import binary
from .types.signatures import Ed25519PublicKey, SPECIFIER_SIZE
from .types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY, UNLOCKHASH_TYPE, UNLOCKHASH_SIZE, UNLOCKHASH_CHECKSUM_SIZE

from JumpScale9 import j
from JumpScale9Lib.clients.rivine import utils
from JumpScale9Lib.clients.rivine.types.transaction import TransactionFactory, DEFAULT_TRANSACTION_VERSION
from JumpScale9Lib.clients.rivine.types.unlockhash import UnlockHash
from JumpScale9Lib.clients.rivine.types.unlockconditions import TIMELOCK_CONDITION_HEIGHT_LIMIT

from .const import MINER_PAYOUT_MATURITY_WINDOW, WALLET_ADDRESS_TYPE, ADDRESS_TYPE_SIZE, HASTINGS_TFT_VALUE

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
        result = None
        url = '{}/explorer'.format(self._bc_network)
        headers = {'user-agent': 'Rivine-Agent'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            msg = 'Failed to get current chain height. {}'.format(response.text)
            logger.error(msg)
            raise RESTAPIError(msg)
        else:
            result = response.json().get('height', None)
            if result is not None:
                result = int(result)
        return result


    def _check_address(self, address, log_errors=True):
        """
        Check if an address is valid
        performs a http call to an explorer to check if an address has (an) (unspent) output(s)

        @param address: Address to check
        @param log_errors: If False, no logging will be executed

        @raises: @RESTAPIError if failed to check address
        """
        result = None
        url = '{}/explorer/hashes/{}'.format(self._bc_network, address)
        headers = {'user-agent': 'Rivine-Agent'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            msg = "Failed to retrieve address information. {}".format(response.text.strip('\n'))
            if log_errors:
                logger.error(msg)
            raise RESTAPIError(msg)
        else:
            result = response.json()
        return result


    def _check_balance(self):
        """
        Syncs the wallet with the blockchain

        @TOCHECK: this needs to be synchronized with locks or other primitive
        """
        current_chain_height = self._get_current_chain_height()
        unconfirmed_txs = self._get_unconfirmed_transactions(format_inputs=True)
        logger.info('Current chain height is: {}'.format(current_chain_height))
        for address in self.addresses:
            # if address in self._addresses_info:
            #     continue
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
                self._collect_transaction_outputs(address=address, transactions=transactions, unconfirmed_txs=unconfirmed_txs)
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
        if blocks is None:
            blocks = {}
        for block_info in blocks:
            if block_info.get('height', None) and block_info['height'] + MINER_PAYOUT_MATURITY_WINDOW >= height:
                logger.info('Ignoring miner payout that has not matured yet')
                continue
            # mineroutputs can exist in the dictionary but with value None
            mineroutputs = block_info.get('rawblock', {}).get('minerpayouts', [])
            if mineroutputs:
                for index, minerpayout in enumerate(mineroutputs):
                    if minerpayout.get('unlockhash') == address:
                        logger.info('Found miner output with value {}'.format(minerpayout.get('value')))
                        self._unspent_coins_outputs[block_info['minerpayoutids'][index]] = {
                            'value': minerpayout['value'],
                            'condition':{
                                'data': {
                                    'unlockhash': address
                                }
                            }
                        }


    def _collect_transaction_outputs(self, address, transactions, unconfirmed_txs=None):
        """
        Collects transactions outputs

        @param address: address to collect transactions outputs
        @param transactions: Details about the transactions
        @param unconfirmed_txs: List of unconfirmed transactions
        """
        if unconfirmed_txs is None:
            unconfirmed_txs = []
        for txn_info in transactions:
            # coinoutputs can exist in the dictionary but has the value None
            coinoutputs = txn_info.get('rawtransaction', {}).get('data', {}).get('coinoutputs', [])
            if coinoutputs:
                for index, utxo in enumerate(coinoutputs):
                    # support both v0 and v1 tnx format
                    if 'unlockhash' in utxo:
                        # v0 transaction format
                        condition_ulh = utxo['unlockhash']
                    elif 'condition' in utxo:
                        # v1 transaction format
                        # check condition type
                        if utxo['condition'].get('type') == 1:
                            # unlockhash condition type
                            condition_ulh = utxo['condition']['data']['unlockhash']
                        elif utxo['condition'].get('type') == 3:
                            # timelock condition, right now we only support timelock condition with internal unlockhash condition
                            locktime = utxo['condition']['data']['locktime']
                            if locktime < TIMELOCK_CONDITION_HEIGHT_LIMIT:
                                # locktime should be checked againest the current chain height
                                current_height = self._get_current_chain_height()
                                if current_height > locktime:
                                    condition_ulh = utxo['condition']['data']['condition']['data'].get('unlockhash')
                                else:
                                    logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                                    continue
                            else:
                                # locktime represent timestamp
                                if locktime < time.time():
                                    condition_ulh = utxo['condition']['data']['condition']['data'].get('unlockhash')
                                else:
                                    logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                                    continue

                    if condition_ulh == address:
                        logger.debug('Found transaction output for address {}'.format(address))
                        if txn_info['coinoutputids'][index] in unconfirmed_txs:
                            logger.warn("Transaction output is part of an unconfirmed tansaction. Ignoring it...")
                            continue
                        self._unspent_coins_outputs[txn_info['coinoutputids'][index]] = utxo


    def _remove_spent_inputs(self, transactions):
        """
        Remvoes the already spent outputs

        @param transactions: Details about the transactions
        """
        for txn_info in transactions:
            # cointinputs can exist in the dict but have the value None
            coininputs = txn_info.get('rawtransaction', {}).get('data', {}).get('coininputs', [])
            if coininputs:
                for coin_input in coininputs:
                    if coin_input.get('parentid') in self._unspent_coins_outputs:
                        logger.debug('Found a spent address {}'.format(coin_input.get('parentid')))
                        del self._unspent_coins_outputs[coin_input.get('parentid')]


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
        result = []
        url = "{}/transactionpool/transactions".format(self._bc_network)
        headers = {'user-agent': 'Rivine-Agent'}
        auth = HTTPBasicAuth('', self._bc_network_password)
        res = requests.get(url, headers=headers, auth=auth)
        if res.status_code != 200:
            msg = 'Failed to retrieve unconfirmed transactions. Error: {}'.format(res.text)
            logger.error(msg)
            raise BackendError(msg)
        transactions = res.json()['transactions']
        if transactions is None:
            transactions = []
        if format_inputs:
            for txn in transactions:
                result.extend([coininput['parentid'] for coininput in txn['data']['coininputs']])
            return result
        return transactions


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
        amount = amount * HASTINGS_TFT_VALUE
        transaction = self._create_transaction(amount=amount,
                                                recipient=recipient,
                                                sign_transaction=True,
                                                custom_data=data,
                                                locktime=locktime)
        self._commit_transaction(transaction=transaction)
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
        if minerfee is None:
            minerfee = self._minerfee
        wallet_fund = self.current_balance * HASTINGS_TFT_VALUE
        required_funds = amount + minerfee
        if required_funds > wallet_fund:
            raise InsufficientWalletFundsError('No sufficient funds to make the transaction')
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)

        # set the the custom data on the transaction
        if custom_data is not None:
            transaction.add_data(custom_data)


        input_value = 0
        for address, unspent_coin_output in self._unspent_coins_outputs.items():
            # if we reach the required funds, then break
            if input_value >= required_funds:
                break

            ulh = unspent_coin_output.get('condition', {}).get('data', {}).get('unlockhash', None)
            if ulh is None:
                # v0 transaction format
                ulh = unspent_coin_output.get('unlockhash', None)
            if ulh is None:
                raise RunimeError('Cannot retrieve unlockhash')

            transaction.add_coin_input(parent_id=address, pub_key=self._keys[unspent_coin_output['condition']['data']['unlockhash']].public_key)

            input_value += int(unspent_coin_output['value'])

        for txn_input in transaction.coins_inputs:
            if self._unspent_coins_outputs[txn_input.parent_id]['condition']['data']['unlockhash'] not in self._keys:
                raise NonExistingOutputError('Trying to spend unexisting output')

        transaction.add_coin_output(value=amount, recipient=recipient, locktime=locktime)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        remainder = input_value - required_funds
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            for address in self._keys.keys():
                used = False
                for unspent_coin_output in self._unspent_coins_outputs.values():
                     if unspent_coin_output['condition']['data']['unlockhash'] == address:
                         used = True
                         break
                if used is True:
                    continue
                transaction.add_coin_output(value=remainder, recipient=address)
                break

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        if sign_transaction:
            # sign the transaction
            self._sign_transaction(transaction)

        return transaction


    def _sign_transaction(self, transaction):
        """
        Signs a transaction with the existing keys.

        @param transaction: Transaction object to be signed
        """
        logger.info("Signing Trasnaction")
        for index, input in enumerate(transaction.coins_inputs):
            key = self._keys[self._unspent_coins_outputs[input.parent_id]['condition']['data']['unlockhash']]
            input.sign(input_idx=index, transaction=transaction, secret_key=key.secret_key)


    def _commit_transaction(self, transaction):
        """
        Commits a singed transaction to the chain

        @param transaction: Transaction object to be committed
        """
        data = transaction.json
        url = '{}/transactionpool/transactions'.format(self._bc_network)
        headers = {'user-agent': 'Rivine-Agent'}
        auth = HTTPBasicAuth('', self._bc_network_password)
        res = requests.post(url, headers=headers, auth=auth, json=data)
        if res.status_code != 200:
            msg = 'Faield to commit transaction to chain network.{}'.format(res.text)
            logger.error(msg)
            raise BackendError(msg)
        else:
            logger.info('Transaction committed successfully')


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
