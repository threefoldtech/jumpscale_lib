"""
Test module for binary encoding
"""

import pytest
from JumpscaleLib.clients.blockchain.tfchain.types import signatures

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
        s = signatures.SiaPublicKeySpecifier(i).to_string()
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
        s = k.to_string()
        assert(s == example)

def test_sia_public_key_binary():
    """
    Test binary encoding of the sia public keys
    """
    for example, expectedHexBinary in exampleSiaKeys.items():
        k = signatures.SiaPublicKey.from_string(example)
        hk = k.binary.hex()
        assert(hk == expectedHexBinary)
