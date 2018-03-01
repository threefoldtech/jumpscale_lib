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

# module level functions (utils)

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
        self._outputs = []
        self._keys = []
        self._bc_network = bc_network
    

    def _generate_spendable_key(self, index):
        """
        Generate a @Spendablekey object from the seed and index
        
        @param index: Index from the seed
        """
    

    def sync_wallet(self):
        """
        Syncs the wallet with the blockchain

        @TOCHECK: this needs to be synchronized with locks or other primitive
        """
    
    
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

    def __init__(self, seed, index):
        """
        Creates new SpendableKey 
        creates the keys and unlock conditions for a given index of a seed
        """
        

class UnlockConditions:
    """
    Represent unlock conditions that would be automatically generated from
    input public key
    """

    def __init__(self, pubkey):
        """
        Generates unlockcontion objects from a public key

        @pubkey: Input public key
        """


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