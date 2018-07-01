"""
Rivine Client
"""

from JumpScale9 import j

from .RivineWallet import RivineWallet


TEMPLATE = """
bc_address = ""
seed_ = ""
nr_keys_per_seed = 50
minerfee = 100000000
password_ = ""
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
            self._wallet = RivineWallet(seed=self.config.data['seed_'],
                                        bc_network=self.config.data['bc_address'],
                                        bc_network_password=self.config.data['password_'],
                                        nr_keys_per_seed=int(self.config.data['nr_keys_per_seed']),
                                        minerfee=int(self.config.data['minerfee']),
                                        client=self.instance)
        return self._wallet
