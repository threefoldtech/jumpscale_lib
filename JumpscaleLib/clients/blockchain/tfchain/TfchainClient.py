"""
Tfchain Client
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.tfchain.TfchainWallet import TfchainWallet
from JumpscaleLib.clients.blockchain.tfchain.TfchainMultiSigWallet import TfchainMultiSignatureWallet

TEMPLATE = """
testnet = false
seed_ = ""
multisig = false
cosigners = []
required_sig = 0
nr_keys_per_seed = 50
"""

JSConfigBase = j.tools.configmanager.JSBaseClassConfig

class TfchainClient(JSConfigBase):
    """
    Constants specific for the Tfchain network
    """
    _tfchain_consts = {
            'standard': {
                'explorers': ['https://explorer.threefoldtoken.com',
                    'https://explorer2.threefoldtoken.com',
                    'https://explorer3.threefoldtoken.com',
                    'https://explorer4.threefoldtoken.com'],
                'password': '',
                'minerfee': 100000000},
            'testnet': {
                'explorers': ['https://explorer.testnet.threefoldtoken.com',
                    'https://explorer2.testnet.threefoldtoken.com'],
                'password': '',
                'minerfee': 100000000}}
    
    """
    Tfchain client object
    """
    def __init__(self, instance, data=None, parent=None, interactive=False):
        """
        Initializes a new Tfchain Client
        """
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance, data=data, parent=parent,
                template=TEMPLATE, interactive=interactive)
        self._wallet = None

    @property
    def wallet(self):
        if self._wallet is None:
            # Load the correct constants regarding testnet or standard net
            consts = self._tfchain_consts['standard']
            if self._config.data['testnet'] is True:
                consts = self._tfchain_consts['testnet']
            if self._config.data['multisig'] is True:
                cosigners = [item.split(',') for item in self.config.data['cosigners']]
                self._wallet = TfchainMultiSignatureWallet(cosigners=cosigners,
                        required_sig=self.config.data['required_sig'],
                        bc_networks = consts['explorers'],
                        bc_network_password = consts['password'],
                        minerfee = consts['minerfee'],
                        client=self.instance)
            else:
                # Load a wallet from a given seed. If no seed is given,
                # generate a new one
                seed = self.config.data['seed_']
                if seed == "":
                    seed = self.generate_seed() 
                    # Save the seed in the config
                    data = dict(self.config.data)
                    data['seed_'] = seed
                    cl = j.clients.tfchain.get(instance=self.instance,
                            data=data,
                            create=True,
                            interactive=False)
                    cl.config.save()
                    # make sure to set the seed in the current object.
                    # if not, we'd have a random non persistent seed until
                    # the first reload
                    self.config.data['seed_'] = seed
                self._wallet = TfchainWallet(seed=seed,
                        bc_networks = consts['explorers'],
                        bc_network_password = consts['password'],
                        nr_keys_per_seed = self.config.data['nr_keys_per_seed'],
                        minerfee = consts['minerfee'],
                        client=self.instance)
        return self._wallet

    def generate_seed(self):
        """
        Generate a new seed
        """
        return j.data.encryption.mnemonic.generate(strength=256) 
