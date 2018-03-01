"""
Rivine Client
"""

from JumpScale9 import j

from .Account import Account


TEMPLATE = """
bc_address = ""
port = 443
seed_ = ""
nr_keys_per_seed = 50
"""



JSConfigBase = j.tools.configmanager.base_class_config


class RivineClient(JSConfigBase):
     """
     Rivine client object
     """
    def __init__(self, instance, data=None, parent=None, interactive=False):
        """"
        Initializes new Rivine Client
        """"
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)
        self._wallet = None


    @property
    def wallet(self):
        if self._wallet is None:
            self._wallet = RivineWallet(seed=self.config.data['seed'],
                                        bc_network=self.config.data['bc_address'],
                                        nr_keys_per_seed=self.config.data['nr_keys_per_seed'])
        return self._wallet