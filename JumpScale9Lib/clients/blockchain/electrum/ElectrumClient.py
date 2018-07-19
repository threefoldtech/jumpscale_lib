"""
JS9 client module that define a client for electrum wallet
"""

from JumpScale9 import j

from .ElectrumWallet import ElectrumWallet


TEMPLATE = """
server = "localhost:7777:s"
rpc_user = "user"
rpc_pass_ = "pass"
seed_ = ""
fee = 10000
password_ = ""
passphrase_ = ""
electrum_path = ""
testnet = 0
"""



JSConfigBase = j.tools.configmanager.base_class_config


class ElectrumClient(JSConfigBase):
    """
    Electrum client object
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
            config_data = {}
            for key, value in self.config.data.items():
                config_data[key.strip('_')] = value
            self._wallet = ElectrumWallet(name=self.instance, config=config_data)
        return self._wallet
