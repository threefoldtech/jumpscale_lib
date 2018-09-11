"""
This module defines the required classes for Tfchain Multisig wallets
"""

from Jumpscale import j
from JumpscaleLib.clients.blockchain.rivine.RivineMultiSigWallet import RivineMultiSignatureWallet

logger = j.logger.get(__name__)

class TfchainMultiSignatureWallet(RivineMultiSignatureWallet):
    """
    TfchainMultiSignatureWallet class
    """
    def __init__(self, cosigners, required_sig, bc_networks, bc_network_password,
            minerfee, client):
        """
        Initializes a new Tfchain MultiSig wallet

        @param cosigners: List of lists, the length of outer list indicates the number of cosigners and the length of the inner lists indicates the number of unlockhashes
        @param required_sig: Minimum number of signatures required for the output sent to any of the Multisig addresses to be spent
        @param bc_networks: List of explorers to use
        @param bc_network_password: Password to send to the explorer node when posting requests.
        @param minerfee: Amount of hastings that should be minerfee (default to 0.1 TFT)
        @param client: Name of the insance of the j.clients.rivine that is used to create the wallet
        """
        super().__init__(cosigners, required_sig, bc_networks, bc_network_password,
                minerfee, client)

