"""
Electrum module to implement atomicswap support
"""
from Jumpscale import j

logger = j.logger.get(__name__)

class ElectrumAtomicswap:
    """
    ElectrumAtomicswap class
    This class wraps the binaries provided by https://github.com/rivine/atomicswap/releases
    """

    def __init__(self, wallet_name, data_dir, rpcuser, rpcpass, rpchost='localhost', rpcport=7777, testnet=False):
        """
        Initialize ElectrumAtomicswap object
        """
        self._prefab = j.tools.prefab.local
        self._wallet_name = wallet_name
        self._data_dir = data_dir
        self._rpcuser = rpcuser
        self._rpcpass = rpcpass
        self._host = '{}:{}'.format(rpchost, rpcport)
        self._testnet = testnet
        self._wallet_path = j.sal.fs.joinPaths(data_dir,
                                              'testnet' if testnet else 'mainnet',
                                              'wallets',
                                              wallet_name)
        self._load_wallet()


    def _load_wallet(self):
        """
        Loads the wallet
        """
        cmd = 'electrum{} -D {} -w {} daemon load_wallet'.format(' --testnet' if self._testnet else '',
                                                                 self._data_dir,
                                                                 self._wallet_path)

        logger.info("Loading wallet {} using command: {}".format(self._wallet_name, cmd))
        self._prefab.core.run(cmd)


    def initiate(self, participant_address, amount):
        """
        Initialize a new atomicswap contract

        @param participant_address: Address of the participant of the contract
        @param amount: amount in BTC to send to participant
        """
        cmd = 'btcatomicswap{} --rpcuser={} --rpcpass={} -s "{}" initiate {} {}'.format(
                    ' -testnet' if self._testnet else '',
                    self._rpcuser,
                    self._rpcpass,
                    self._host,
                    participant_address,
                    amount
        )
        logger.info("Initiating a new atomicswap contract using command: {}".format(cmd))
        self._prefab.core.run(cmd)
