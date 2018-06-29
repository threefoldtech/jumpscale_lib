"""
Unittests for JumpScale9Lib.clients.rivine.types.signatures module
"""

import ed25519
from JumpScale9Lib.clients.rivine.types.signatures import Ed25519PublicKey


def test_Ed25519PublicKey_binary():
    """
    Tests generating binary encoded version of a Ed25519Ed25519PublicKey
    """
    expected_output = bytearray(b'ed25519\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    _, pk = ed25519.create_keypair(entropy=lambda x: b'a'*64)
    ed25519_key = Ed25519PublicKey(pub_key=pk.to_bytes())
    assert ed25519_key.binary == expected_output, "Ed25519PublicKey does not produce the correct binary value"


def test_Ed25519PublicKey_json():
    """
    Tests generating json encoded version of a Ed25519Ed25519PublicKey
    """
    expected_output = 'ed25519:6161616161616161616161616161616161616161616161616161616161616161'
    _, pk = ed25519.create_keypair(entropy=lambda x: b'a'*64)
    ed25519_key = Ed25519PublicKey(pub_key=pk.to_bytes())
    assert ed25519_key.json == expected_output, "Ed25519PublicKey does not produce the correct binary value"
