"""
JS9 module provides an electrum wallet functionalities
"""

import os
from electrum import daemon
from electrum import keystore
from electrum.wallet import Wallet
from electrum.network import Network
from electrum.commands import Commands
from electrum.storage import WalletStorage
from electrum.simple_config import SimpleConfig


class ElectrumWallet:
    """
    An Electrum wallet wrapper
    """

    def __init__(self, name, config):
        """
        Initializes new electrum wallet instance

        @param name: Name of the wallet
        @param config: Configuration dictionary e.g {
            'server': 'localhost:7777:s',
            'rpc_user': 'user',
            'rpc_pass_': 'pass',
            'electrum_path': '/opt/var/data/electrum',
            'seed': '....',
            'fee': 10000,
            'testnet': 1
        }
        """
        self._name = name
        self._config = config
        self._electrum_config = SimpleConfig(self._config)
        self._wallet_path = os.path.join(self._electrum_config.path, 'wallets', self._name)
        self._storage = WalletStorage(path=self._wallet_path)
        self._electrum_config.set_key('default_wallet_path', self._wallet_path)
        k = keystore.from_seed(self._config['seed'], self._config['passphrase'], False)
        k.update_password(None, self._config['password'])
        self._storage.put('keystore', k.dump())
        self._storage.put('wallet_type', 'standard')
        self._storage.put('use_encryption', bool(self._config['password']))
        self._storage.write()
        self._wallet = Wallet(self._storage)
        # self._wallet.update_password(None, self._config['password'], True)
        self._wallet.synchronize()
        self._server = daemon.get_server(self._electrum_config)
        self._network = None
        self._commands = Commands(config=self._electrum_config,
                                  wallet=self._wallet,
                                  network=self._get_network())


    def _get_network(self):
        """
        Get/Create a network object
        """
        if self._network is None:
            self._network = Network(self._electrum_config)
        return self._network
