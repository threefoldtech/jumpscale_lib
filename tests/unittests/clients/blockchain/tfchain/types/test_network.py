"""
Test module for binary encoding
"""

import pytest
from JumpscaleLib.clients.blockchain.tfchain.types import network

# examples and expected binary-hex encoded strings taken from
# the tfchain Go reference implementation (github.com/threefoldfoundation/tfchain)
tfchainExampleNetworkAddresses = {
    "0.0.0.1": "1100000001",
    "127.0.0.1": "117f000001",
    "network.address.com": "4c6e6574776f726b2e616464726573732e636f6d",
    "83.200.201.201": "1153c8c9c9",
    "2001:db8:85a3::8a2e:370:7334": "4220010db885a3000000008a2e03707334",
}

def test_network_address_string():
    """
    Test string encoding and decoding of the network addresses
    """
    for example in tfchainExampleNetworkAddresses:
        na = network.NetworkAddress.from_string(example)
        s = str(na)
        assert(s == example)

def test_network_address_binary():
    """
    Test binary encoding and decoding of the network addresses
    """
    for example, expectedBinaryHexFormat in tfchainExampleNetworkAddresses.items():
        na = network.NetworkAddress.from_string(example)
        bh = na.binary.hex()
        assert(bh == expectedBinaryHexFormat)
