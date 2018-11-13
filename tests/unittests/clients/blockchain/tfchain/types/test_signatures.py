"""
Test module for binary encoding
"""

import pytest
from JumpscaleLib.clients.blockchain.tfchain.types import signatures
from JumpscaleLib.clients.blockchain.rivine.types import signatures as rsignatures
from JumpscaleLib.clients.blockchain.rivine.encoding import binary as rbinary

tfchainSignatureAlgoSpecifiers = {
    0: "",
    1: "ed25519",
}

def test_signature_algorithm_specifiers_binary():
    """
    Test binary encoding of the signature algorithm specifiers
    """
    for i in tfchainSignatureAlgoSpecifiers:
        bs = signatures.SiaPublicKeySpecifier(i).binary
        assert(bs is not i or len(bs) != 1)

def test_signature_algorithm_specifiers_string():
    """
    Test string encoding of the signature algorithm specifiers
    """
    for i, expected_specifier in tfchainSignatureAlgoSpecifiers.items():
        s = str(signatures.SiaPublicKeySpecifier(i))
        assert(expected_specifier == s)
        specifier = signatures.SiaPublicKeySpecifier.from_string(s)
        assert(i == specifier)

# examples and expected binary-hex encoded strings taken from
# the tfchain Go reference implementation (github.com/threefoldfoundation/tfchain)
exampleSiaKeys = {
    "ed25519:97d784b93d5769d2df0010b793622eae14a33992b958e8406cceb827a8101d29": "0197d784b93d5769d2df0010b793622eae14a33992b958e8406cceb827a8101d29",
    "ed25519:cb859ec8da13d0bcfc7b1c3c8e6647b5510791eda3a74ba1bba4954a8c74e4a9": "01cb859ec8da13d0bcfc7b1c3c8e6647b5510791eda3a74ba1bba4954a8c74e4a9",
    "ed25519:857c029d8689c97d51f314e1a4e6a4543c42a696ee93ce848d1247bf24eb52a3": "01857c029d8689c97d51f314e1a4e6a4543c42a696ee93ce848d1247bf24eb52a3",
    "ed25519:4683705f729a65e9e133e1719d05ad8ac45a14e44fcf6c85de19e5ac7fcd2e9d": "014683705f729a65e9e133e1719d05ad8ac45a14e44fcf6c85de19e5ac7fcd2e9d",
}

def test_sia_public_key_string():
    """
    Test string encoding and decoding of the sia public keys
    """
    for example in exampleSiaKeys:
        k = signatures.SiaPublicKey.from_string(example)
        s = str(k)
        assert(s == example)

def test_sia_public_key_binary():
    """
    Test binary encoding of the sia public keys
    """
    for example, expectedHexBinary in exampleSiaKeys.items():
        k = signatures.SiaPublicKey.from_string(example)
        hk = k.binary.hex()
        assert(hk == expectedHexBinary)

# taken from tfchain testnet and devnet
exampleTfchainPublicUnlockHashes= {
    'ed25519:9e095c02584a5b042dfcf679837c88be924c40c95f173fe24d96852f6fd8c193': '01bebecb3acb74852cf50691a5be41785f1fd040a6594be203c7df1d13b398cfd77786a247e909',
    'ed25519:846bc547599b9ed6f686fd1bca39e8fc5524559b559081ec7bb76b6a7e5c2218': '0165c4d7cf3c52cab81fd7e82cd9e39d7fb8a1c7ab7515ac904299495244d0822c15841672f205',
    'ed25519:8f9812bfebb5b95ee25b94c9600ed8061356c8885c67dd5eae832535a6c5ef2d': '01a56161fbd36275f870a322afa60656a10d8d8a179bf55b17804f098c46b50da25c23ccdf5bc3',
}
def test_sia_public_key_rivine_binary():
    """
    Test the unlock_hash property of the (tfchain implementation) of the sia public key
    """
    for example in exampleTfchainPublicUnlockHashes:
        k = signatures.SiaPublicKey.from_string(example)
        rk = rsignatures.SiaPublicKeyFactory.from_string(example)
        tfb = k.rivine_binary.hex()
        rivb = rbinary.encode(rk).hex()
        assert(tfb == rivb)
def test_sia_public_key_unlockhash():
    """
    Test the unlock_hash property of the (tfchain implementation) of the sia public key
    """
    for example, expectedUnlockHash in exampleTfchainPublicUnlockHashes.items():
        k = signatures.SiaPublicKey.from_string(example)
        uh = str(k.unlock_hash)
        rk = rsignatures.SiaPublicKeyFactory.from_string(example)
        rbinary.encode(rk).hex()
        assert(uh == expectedUnlockHash)
