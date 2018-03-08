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
import merkletools
import hashlib
import requests

from JumpScale9 import j

from .const import SIGEd25519, UNLOCKHASHTYPE, MINERPAYOUTMATURITYWINDOW
from .errors import RESTAPIError, BACKENDError

logger = j.logger.get(__name__)

class RivineWallet:
    """
    Wallet class
    """
    def __init__(self, seed, bc_network, nr_keys_per_seed=50):
        """
        Creates new wallet
        TODO: check if we need to support multiple seeds from the begining
        
        @param seed: Starting point seed to generate keys
        @param bc_network: Blockchain network to use.
        @param nr_keys_per_seed: Number of keys generated from the seed.
        """ 
        self._seed = seed
        self._unspent_coins_outputs = {}
        self._keys = {}
        # self._bc_network = '{}/explorer/'.format(bc_network) if \
        #                         not bc_network.endswith('explorer') else bc_network
        self._bc_network = bc_network
        for index in range(nr_keys_per_seed):
            key = self._generate_spendable_key(index=index)
            self._keys[key.unlockconditions.unlockhash] = key
    

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
        return SpendableKey(seed=binary_seed)


    def get_current_chain_height(self):
        """
        Retrieves the current chain height
        """
        result = None
        url = '{}/explorer'.format(self._bc_network)
        response = requests.get(url)
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
        response = requests.get(url)
        if response.status_code != 200:
            msg = "Failed to retrieve address information. {}".format(response.text)
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
            address_info = self.check_address(address=address)
            if address_info.get('hashtype', None) != UNLOCKHASHTYPE:
                raise BACKENDError('Address is not recognized as an unblock hash')
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
        for block_info in blocks:
            if block_info.get('height', None) and block_info['height'] + MINERPAYOUTMATURITYWINDOW >= height:
                logger.info('Ignoring miner payout that has not matured yet')
                continue
            # mineroutputs can exist in the dictionary but with value None
            mineroutputs = block_info.get('rawblock', {}).get('minerpayouts', [])
            if mineroutputs:
                for index, minerpayout in enumerate(mineroutputs):
                    if minerpayout.get('unlockhash') == address:
                        logger.info('Found miner output with value {}'.format(minerpayout.get('value')))
                        self._unspent_coins_outputs[block_info['minerpayoutids'][index]] = minerpayout.get('value')


    
    def _collect_transaction_outputs(self, address, transactions):
        """
        Collects transactions outputs

        @param address: address to collect transactions outputs
        @param transactions: Details about the transactions
        """
        for txn_info in transactions:
            # coinoutputs can exist in the dictionary but has the value None
            coinoutputs = txn_info.get('rawtransaction', {}).get('coinoutputs', [])
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
            coininputs = txn_info.get('rawtransaction', {}).get('coininputs', [])
            if coininputs:
                for coin_input in coininputs:
                    if coin_input.get('parentid') in self._unspent_coins_outputs:
                        logger.info('Found a spent address {}'.format(coin_input.get('parentid')))
                        del self._unspent_coins_outputs[coin_input.get('parentid')]


    def create_transaction(amount, recipient):
        """
        Creates new transaction and sign it

        @param amount: The amount needed to be transfered
        @param recipient: Address of the recipient.
        """

    
    def _sing_transaction(self, transaction):
        """
        Sings a transaction with the existing keys.
        
        @param transaction: Transaction object to be signed
        """

    

    def commit_transaction(self, transaction):
        """
        Commits a singed transaction to the chain

        @param transaction: Transaction object to be committed
        """
        


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
        self._pk = self._sk.get_verifying_key()
        self._unlockconditions = UnlockConditions(pubkey=self._pk)
    
    @property
    def secretkeys(self):
        """
        Returns the singing keys
        """
        return [self._sk]
    
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
        self._merkletree = merkletools.MerkleTools()
        self._unlockhash = None
    

    @property
    def unlockhash(self):
        """
        Get a lockhash of the current UnlockConditions
        UnlockHash calculates the root hash of a Merkle tree of the
        UnlockConditions object. The leaves of this tree are formed by taking the
        hash of the timelock, the hash of the public keys (one leaf each), and the
        hash of the number of signatures. The keys are put in the middle because
        Timelock and SignaturesRequired are both low entropy fields; they can bee
        protected by having random public keys next to them.
        """
        if self._unlockhash is None:
            values = []
            values.append(hashlib.blake2b(self._blockheight.to_bytes(4, byteorder='big')).hexdigest())
            for key in self._keys:
                values.append(hashlib.blake2b(key['key'].to_bytes(prefix='')).hexdigest())
            values.append(hashlib.blake2b(self._nr_required_sigs.to_bytes(4, byteorder='big')).hexdigest())
            self._merkletree.add_leaf(values=values, do_hash=False)
            self._merkletree.make_tree()
            self._unlockhash = self._merkletree.get_merkle_root()

        return self._unlockhash
        



class Transaction:
    """
    Represent a Transaction of funds from inputs to outputs
    """

    def __init__(self):
        """
        Initialize new transaction
        """
        self._inputs = []
        self._output = []