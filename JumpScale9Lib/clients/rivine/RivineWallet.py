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

from mnemonic import Mnemonic
import ed25519
from .merkletree import Tree
from pyblake2 import blake2b
from functools import partial
import requests
import base64
from requests.auth import HTTPBasicAuth
from .utils import big_int_to_binary, int_to_binary, get_unlockhash_from_address

from JumpScale9 import j

from .const import SIGEd25519, UNLOCKHASH_TYPE, MINER_PAYOUT_MATURITY_WINDOW,\
UNLOCKHASH_SIZE, UNLOCKHASH_CHECKSUM_SIZE, SPECIFIER_SIZE, NON_SIA_SPECIFIER, WALLET_ADDRESS_TYPE, ADDRESS_TYPE_SIZE

from .errors import RESTAPIError, BackendError,\
InsufficientWalletFundsError, NonExistingOutputError,\
NotEnoughSignaturesFound, InvalidUnlockHashChecksumError

logger = j.logger.get(__name__)

class RivineWallet:
    """
    Wallet class
    """
    def __init__(self, seed, bc_network, bc_network_password, nr_keys_per_seed=50, minerfee=10):
        """
        Creates new wallet
        TODO: check if we need to support multiple seeds from the begining

        @param seed: Starting point seed to generate keys.
        @param bc_network: Blockchain network to use.
        @param bc_network_password: Password to send to the explorer node when posting requests.
        @param nr_keys_per_seed: Number of keys generated from the seed.
        @param minerfee: Amount of hastings that should be minerfee.
        """
        self._seed = seed
        self._unspent_coins_outputs = {}
        self._keys = {}
        self._bc_network = bc_network.strip("/")
        self._minerfee = minerfee
        self._bc_network_password = bc_network_password
        # needed to avoid calculating addresses from unlock hashes later
        self._unlockhash_key_map = {}
        self._unlockhash_address_map = {}
        for index in range(nr_keys_per_seed):
            key = self._generate_spendable_key(index=index)
            address = self._generate_address(key.unlockconditions.unlockhash)
            self._keys[address] = key
            self._unlockhash_key_map[key.unlockconditions.unlockhash] = key
            self._unlockhash_address_map[address] = key.unlockconditions.unlockhash
        self._addresses = None


    def _generate_address(self, unlockhash):
        """
        Generate a public address from unlockhash

        @param unlockhash: Source unlockhash to create an address from it
        """
        key_bytes = bytearray.fromhex(unlockhash)
        key_bytes = WALLET_ADDRESS_TYPE + key_bytes
        key_hash = blake2b(key_bytes, digest_size=UNLOCKHASH_SIZE).digest()
        return '{}{}{}'.format(WALLET_ADDRESS_TYPE.hex(), unlockhash, key_hash[:UNLOCKHASH_CHECKSUM_SIZE].hex())


    @property
    def addresses(self):
        """
        Wallet addresses to recieve and send funds
        """
        return [key for key in self._keys.keys()]


    @property
    def keys(self):
        """
        Set of SpendableKeys
        """
        return self._keys

    @property
    def unspent_coins_outputs(self):
        """
        The unspent coins outputs
        """
        return self._unspent_coins_outputs


    def _generate_spendable_key(self, index):
        """
        Generate a @Spendablekey object from the seed and index

        @param index: Index from the seed
        """
        # the to_seed function will return a 64 bytes binary seed, we only need 32-bytes
        binary_seed = Mnemonic.to_seed(mnemonic=self._seed, passphrase=str(index))[32:]
        binary_seed_hash = blake2b(binary_seed, digest_size=32).digest()
        return SpendableKey(seed=binary_seed_hash)


    def get_current_chain_height(self):
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


    def check_address(self, address):
        """
        Check if an address is valid
        performs a http call to an explorer to check if an address has (an) (unspent) output(s)

        @param address: Address to check
        """
        result = None
        url = '{}/explorer/hashes/{}'.format(self._bc_network, address)
        headers = {'user-agent': 'Rivine-Agent'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            msg = "Failed to retrieve address information. {}".format(response.text.strip('\n'))
            logger.error(msg)
            raise RESTAPIError(msg)
        else:
            result = response.json()
        return result


    def sync_wallet(self):
        """
        Syncs the wallet with the blockchain

        @TOCHECK: this needs to be synchronized with locks or other primitive
        """
        current_chain_height = self.get_current_chain_height()
        logger.info('Current chain height is: {}'.format(current_chain_height))
        for address in self._keys.keys():
            try:
                address_info = self.check_address(address=address)
            except RESTAPIError as ex:
                logger.error('Skipping address: {}'.format(address))
            else:
                if address_info.get('hashtype', None) != UNLOCKHASH_TYPE:
                    raise BackendError('Address is not recognized as an unblock hash')
                self._collect_miner_fees(address=address, blocks=address_info.get('blocks',{}),
                                        height=current_chain_height)
                transactions = address_info.get('transactions', {})
                self._collect_transaction_outputs(address=address, transactions=transactions)
                self._remove_spent_inputs(transactions=transactions)


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
                        self._unspent_coins_outputs[block_info['minerpayoutids'][index]] = minerpayout



    def _collect_transaction_outputs(self, address, transactions):
        """
        Collects transactions outputs

        @param address: address to collect transactions outputs
        @param transactions: Details about the transactions
        """
        for txn_info in transactions:
            # coinoutputs can exist in the dictionary but has the value None
            coinoutputs = txn_info.get('rawtransaction', {}).get('data', {}).get('coinoutputs', [])
            if coinoutputs:
                for index, utxo in enumerate(coinoutputs):
                    if utxo.get('unlockhash') == address:
                        logger.info('Found transaction output for address {}'.format(address))
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
                        logger.info('Found a spent address {}'.format(coin_input.get('parentid')))
                        del self._unspent_coins_outputs[coin_input.get('parentid')]


    def create_transaction(self, amount, recipient, minerfee=None, sign_transaction=True, custom_data=None):
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
        """
        if minerfee is None:
            minerfee = self._minerfee
        wallet_fund = sum(int(value.get('value')) for value in self._unspent_coins_outputs.values())
        required_funds = amount + minerfee
        if required_funds > wallet_fund:
            raise InsufficientWalletFundsError('No sufficient funds to make the transaction')
        transaction = Transaction()

        # set the the custom data on the transaction
        if custom_data is not None:
            transaction.custom_data = custom_data

        input_value = 0
        for address, unspent_coin_output in self._unspent_coins_outputs.items():
            # if we reach the required funds, then break
            if input_value >= required_funds:
                break
            transaction.add_input({'parentid': address,
                                    'unlockconditions': self._keys[unspent_coin_output['unlockhash']].unlockconditions})
            input_value = int(unspent_coin_output['value'])

        for txn_input in transaction.inputs:
            if self._unspent_coins_outputs[txn_input['parentid']]['unlockhash'] not in self._keys.keys():
                raise NonExistingOutputError('Trying to spend unexisting output')

        transaction.add_output({'value': amount,
                                'unlockhash': recipient})

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        remainder = input_value - required_funds
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            for address in self._keys.keys():
                used = False
                for unspent_coin_output in self._unspent_coins_outputs.values():
                     if unspent_coin_output['unlockhash'] == address:
                         used = True
                         break
                if used is True:
                    continue
                transaction.add_output({'value': remainder,
                                        'unlockhash': address})
                break

        # add minerfee to the transaction
        transaction.minerfee = minerfee

        if sign_transaction:
            # sign the transaction
            self._sign_transaction(transaction)

        return transaction


    def _sign_transaction(self, transaction):
        """
        Signs a transaction with the existing keys.

        @param transaction: Transaction object to be signed
        """
        covered_fields = {'wholetransaction': True}
        # add a signature for every input
        for input_ in transaction.inputs:
            key = self._unlockhash_key_map[input_['unlockconditions'].unlockhash]
            self._add_signatures(transaction=transaction,
                                 covered_fields=covered_fields,
                                 unlock_conditions=input_['unlockconditions'],
                                 parent_id=input_['parentid'],
                                 spendable_key=key)


    def _add_signatures(self, transaction, covered_fields, unlock_conditions, parent_id, spendable_key):
        """
        Add a signture to a transaction using one of the spendable keys
        with support for multisig spendable keys. Because of the restricted input, the function
        is compatible with both coin inputs and blockstake inputs.
        Try to find the matching secret key for each public key - some public
        keys may not have a match. Some secret keys may be used multiple times,
	    which is why public keys are used as the outer loop.
        """
        total_signatures = 0
        for index, publickey in enumerate(unlock_conditions.public_keys):
            # search for the matching secret key to the public key
            for secret_key, pkey in spendable_key.secretkeys:
                if pkey != publickey:
                    continue

                # found a matching secret key, create a signature and add it
                signature = {
                    'parentid': parent_id,
                    'coveredfields': covered_fields,
                    'publickeyindex': index,
                    'timelock': 0,
                    'signature': bytearray()

                }
                signature_hash = transaction.get_signature_hash(signature, self._unlockhash_address_map)
                # logger.info('Singature_hash is: {}'.format(len(signature_hash)))
                signature['signature'] = base64.b64encode(secret_key.sign(signature_hash)).decode('ascii')
                total_signatures += 1
                transaction.add_signature(signature)
                break
            # if we got enough signatrues then we break
            if total_signatures == unlock_conditions.nr_required_signatures:
                break
        if total_signatures < unlock_conditions.nr_required_signatures:
            raise NotEnoughSignaturesFound('Not enough keys found to satisfy required number of signatures')



    def commit_transaction(self, transaction):
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
    SpendableKey is a set of secret keys plus the corresponding unlock
    conditions.  The public key can be derived from the secret key and then
    matched to the corresponding public keys in the unlock conditions.
    """

    def __init__(self, seed):
        """
        Creates new SpendableKey
        creates the keys and unlock conditions for 32-bytes seed

        @param seed: A 32-bytes binary seed
        @type seed: bytearray
        """
        # this will generate a singing key based on the seed and from the singing key, the public key/
        # verification key can be retrieved
        self._seed = seed
        self._sk = ed25519.SigningKey(self._seed)
        self._keys = [(self._sk,  self._sk.get_verifying_key().to_bytes())]
        self._unlockconditions = UnlockConditions(pubkey=self._sk.get_verifying_key().to_bytes())


    @property
    def secretkeys(self):
        """
        Returns the singing keys
        """
        return self._keys


    @property
    def unlockconditions(self):
        return self._unlockconditions


class UnlockConditions:
    """
    Represent unlock conditions that would be automatically generated from
    input public key
    """

    def __init__(self, pubkey, nr_required_sigs=1):
        """
        Generates unlockcontion objects from a public key

        @param pubkey: Input public key
        @param nr_required_sings: Number of required singnatures
        """
        self._keys = [{
            'algorithm': SIGEd25519,
            'key': pubkey
        }]
        self._nr_required_sigs = nr_required_sigs
        self._blockheight = 0
        self._merkletree = Tree(hash_func=partial(blake2b, digest_size=UNLOCKHASH_SIZE))
        self._unlockhash = None
        self._binary = None
        self._json = None


    @property
    def public_keys(self):
        """
        Retrieve the public keys of the unlock conditions
        """
        return [item['key'] for item in self._keys]


    @property
    def nr_required_signatures(self):
        """
        Number of required singatures
        """
        return self._nr_required_sigs


    @property
    def unlockhash(self):
        """
        Get the  unlockhash of the current UnlockConditions
        UnlockHash calculates the root hash of a Merkle tree of the
        UnlockConditions object. The leaves of this tree are formed by taking the
        hash of the timelock, the hash of the public keys (one leaf each), and the
        hash of the number of signatures. The keys are put in the middle because
        Timelock and SignaturesRequired are both low entropy fields; they can bee
        protected by having random public keys next to them.
        """
        if self._unlockhash is None:
            self._merkletree.push(int_to_binary(self._blockheight))
            # logger.info("Pushing {}".format(int_to_binary(self._blockheight).hex()))
            for key in self._keys:
                key_value = bytearray()
                s = bytearray(SPECIFIER_SIZE)
                s[:len(key['algorithm'])] = bytearray(key['algorithm'], encoding='utf-8')
                key_value.extend(s)
                key_value.extend(int_to_binary(len(key['key'])))
                key_value.extend(key['key'])
                self._merkletree.push(bytes(key_value))
                # logger.info('Pushing {}'.format(key_value.hex()))
            self._merkletree.push(bytes(int_to_binary(self._nr_required_sigs)))
            # logger.info('Pushing {}'.format(int_to_binary(self._nr_required_sigs).hex()))
            self._unlockhash = self._merkletree.root().hex()

        return self._unlockhash


    @property
    def binary(self):
        """
        Result of serializing the data attributes to a bytearray
        """
        if self._binary is None:
            self._binary = bytearray()
            self._binary.extend(int_to_binary(self._blockheight))
            # encode the number of the keys
            self._binary.extend(int_to_binary(len(self._keys)))
            for key in self._keys:
                # encode specifier
                s = bytearray(SPECIFIER_SIZE)
                s[:len(key['algorithm'])] = bytearray(key['algorithm'], encoding='utf-8')
                self._binary.extend(s)
                # encode the size of the key
                self._binary.extend(int_to_binary(len(key['key'])))
                self._binary.extend(key['key'])
            self._binary.extend(int_to_binary(self._nr_required_sigs))
        return bytes(self._binary)


    @property
    def json(self):
        """
        Return a json encoded representation of the unlockconditions object
        This will return a presentation of the unlocker attribute of the transaction as a singleSingatureInputLock
        """
        if self._json is None:
            public_keys = []
            condition = {
                'publickey': '{}:{}'.format(self._keys[0]['algorithm'],
                                            base64.b64encode(self._keys[0]['key']).decode('ascii'))
            }
            self._json = {
                'type': 1,
                'condition': condition,
                'fulfillment': {
                    'signature': ''
                }
            }

            # for pkey in self._keys:
            #     public_keys.append({
            #         'algorithm': pkey['algorithm'],
            #         'key': base64.b64encode(pkey['key']).decode('ascii')
            #     })
            #
            # self._json = {
            #     'timelock': self._blockheight,
            #     'publickeys': public_keys,
            #     'signaturesrequired': self._nr_required_sigs
            # }

        return self._json


class Transaction:
    """
    Represent a Transaction of funds from inputs to outputs
    """

    def __init__(self):
        """
        Initialize new transaction
        """
        self._inputs = []
        self._outputs = []
        self._minerfee = 0
        self._blockstake_inputs = []
        self._blockstake_outputs = []
        self._arbitrary_data = None
        self._signatrues = []
        self._json = None


    @property
    def signatrues(self):
        """
        Transaction signatures
        """
        return self._signatrues


    @property
    def inputs(self):
        """
        Inputs of the transactions
        """
        return self._inputs


    @property
    def outputs(self):
        """
        Outputs of the transactions
        """
        return self._outputs


    @property
    def minerfee(self):
        """
        The miner fee of the transaction
        """
        return self._minerfee


    @minerfee.setter
    def minerfee(self, value):
        """
        Sets the miner fee
        """
        self._minerfee = value

    @property
    def custom_data(self):
        """
        Transaction custom data
        """
        return self._arbitrary_data


    @custom_data.setter
    def custom_data(self, data):
        """
        Set the transaction cutom data
        """
        # eventually aribitrary data should be a 2d array
        # we also need to to prepend the data with a nonsia specificer
        data_ = bytearray(SPECIFIER_SIZE)
        data_[:len(NON_SIA_SPECIFIER)] = bytearray(NON_SIA_SPECIFIER, encoding='utf-8')
        # data_ = bytearray(NON_SIA_SPECIFIER, encoding='utf-8')
        data_.extend(data)
        self._arbitrary_data = [data_]


    @property
    def json(self):
        """
        JSON encoded representation of the transaction
        For reference: https://github.com/rivine/rivine/blob/master/doc/transactions/transaction.md
        """
        if self._json is None:
            self._json = {
            'version': 0,
            'data': {}
            }
            inputs = []
            for input_ in self._inputs:
                inputs.append({
                    'parentid': input_['parentid'],
                    'unlocker': input_['unlockconditions'].json,
                })
            self._json['data']['coininputs'] = inputs
            outputs = []
            for output in self._outputs:
                outputs.append({
                    'value': str(output['value']),
                    'unlockhash': output['unlockhash'],
                })
            self._json['data']['coinoutputs'] = outputs
            self._json['data']['minerfees'] = [str(self._minerfee)]
            if self._arbitrary_data is not None:
                arbitrary_data_json = []
                for item in self._arbitrary_data:
                    arbitrary_data_json.append(base64.b64encode(item).decode('ascii'))
                self._json['data']['arbitrarydata'] = arbitrary_data_json
            else:
                self._json['data']['arbitrarydata'] = self._arbitrary_data
            self._json['data']['blockstakeinputs'] = None
            self._json['data']['blockstakeoutputs'] = None
            transaction_signatures = []
            for txn_sig in self._signatrues:
                signature = {
                    'parentid': txn_sig['parentid'],
                    # 'parentid':  base64.b64encode(txn_sig['parentid']).decode('ascii'),
                    'publickeyindex': txn_sig['publickeyindex'],
                    'timelock': txn_sig['timelock'],
                    'coveredfields':{
                        'wholetransaction': True,
                        'coininputs': None,
                        'coinoutputs': None,
                        'blockstakeinputs': None,
                        'blockstakeoutputs': None,
                        'minerfees': None,
                        'arbitrarydata': None,
                        'transactionsignatures': None,

                    },
                    'signature': txn_sig['signature'],
                }
                transaction_signatures.append(signature)

            self._json['data']['transactionsignatures'] = transaction_signatures

        return self._json


    def add_input(self, input_info):
        """
        Adds new input to the transaction
        """
        self._inputs.append(input_info)


    def add_output(self, output_info):
        """
        Adds a new output to the transaction
        """
        self._outputs.append(output_info)


    def add_signature(self, signature):
        """
        Adds a new signature to the transaction

        @param signature: signature details
        """
        self._signatrues.append(signature)


    def get_signature_hash(self, signature, unlockhash_address_map):
        """
        Calculates the hash of a signature
        currently only support whole_transaction: True
        """
        signature_hash = bytearray()
        if signature.get('coveredfields', False):
            # for the inputs we need to encode the lenght first
            signature_hash.extend(int_to_binary(len(self._inputs)))
            for input_ in self._inputs:
                signature_hash.extend(bytearray.fromhex(input_['parentid']))
                signature_hash.extend(input_['unlockconditions'].binary)
            # encode the number of the outputs
            signature_hash.extend(int_to_binary(len(self._outputs)))
            for output in self._outputs:
                signature_hash.extend(big_int_to_binary(output['value']))

                # check if the unlockhash already exist in the caching map, otherwise generate
                # an unlock hash without the checksum
                unlockhash = unlockhash_address_map.get(output['unlockhash'], get_unlockhash_from_address(output['unlockhash']))
                signature_hash.extend(bytearray.fromhex(unlockhash))

            # encode the number of the blockstake inputs
            signature_hash.extend(int_to_binary(len(self._blockstake_inputs)))
            for input_ in self._blockstake_inputs:
                signature_hash.extend(bytearray.fromhex(input_['parentid']))
                signature_hash.extend(input_['unlockconditions'].binary)

            # encode the number of the blockstake outputs
            signature_hash.extend(int_to_binary(len(self._blockstake_outputs)))
            for output in self._blockstake_outputs:
                signature_hash.extend(big_int_to_binary(output['value']))
                # check if the unlockhash already exist in the caching map, otherwise generate
                # an unlock hash without the checksum
                unlockhash = unlockhash_address_map.get(output['unlockhash'], get_unlockhash_from_address(output['unlockhash']))
                signature_hash.extend(bytearray.fromhex(unlockhash))

            # for now we only set the nubmer of minerfees to 1
            signature_hash.extend(int_to_binary(1))
            signature_hash.extend(big_int_to_binary(self._minerfee))

            # encode the size of the arbitrary data
            if self._arbitrary_data is not None:
                signature_hash.extend(int_to_binary(len(self._arbitrary_data)))
                for item in self._arbitrary_data:
                    signature_hash.extend(int_to_binary(len(item)))
                    signature_hash.extend(item)
            else:
                signature_hash.extend(int_to_binary(0))

            signature_hash.extend(bytearray.fromhex(signature['parentid']))
            signature_hash.extend(int_to_binary(signature['publickeyindex']))
            signature_hash.extend(int_to_binary(signature['timelock']))
        logger.debug('Signature hash size is {}'.format(len(signature_hash)))
        return blake2b(signature_hash, digest_size=UNLOCKHASH_SIZE).digest()
