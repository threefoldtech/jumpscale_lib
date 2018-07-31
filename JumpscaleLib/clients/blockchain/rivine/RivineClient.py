"""
Rivine Client
"""

from JumpScale9 import j

from JumpScale9Lib.clients.blockchain.rivine.RivineWallet import RivineWallet
from JumpScale9Lib.clients.blockchain.rivine.RivineMultiSigWallet import RivineMultiSignatureWallet


TEMPLATE = """
bc_address = ""
seed_ = ""
nr_keys_per_seed = 50
minerfee = 100000000
password_ = ""
multisig = false
cosigners = []
required_sig = 0
"""



JSConfigBase = j.tools.configmanager.base_class_config


class RivineClient(JSConfigBase):
    """
    Rivine client object
    """
    def __init__(self, instance, data=None, parent=None, interactive=False):
        """
        Initializes new Rivine Client
        """
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)
        self._wallet = None


    @property
    def wallet(self):
        if self._wallet is None:
            if self._config.data['multisig'] is True:
                # due to a bug in config manager we cannot store cosigners as list of lists in the toml config file
                # that is why we store it as list of a comma separated list of items, here we have to load it into list of lists
                cosigners = [item.split(',') for item in self.config.data['cosigners']]
                self._wallet = RivineMultiSignatureWallet(cosigners=cosigners,
                                                        required_sig=self.config.data['required_sig'],
                                                        bc_network=self.config.data['bc_address'],
                                                        bc_network_password=self.config.data['password_'],
                                                        minerfee=int(self.config.data['minerfee']),
                                                        client=self.instance)
            else:
                self._wallet = RivineWallet(seed=self.config.data['seed_'],
                                            bc_network=self.config.data['bc_address'],
                                            bc_network_password=self.config.data['password_'],
                                            nr_keys_per_seed=int(self.config.data['nr_keys_per_seed']),
                                            minerfee=int(self.config.data['minerfee']),
                                            client=self.instance)
        return self._wallet
