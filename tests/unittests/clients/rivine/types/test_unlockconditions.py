"""
Unittests for module JumpScale9Lib.clients.rivine.types.unlockconditions
"""

from JumpScale9Lib.clients.rivine.types.unlockconditions import UnlockHashCondition, LockTimeCondition, SingleSignatureFulfillment
from JumpScale9Lib.clients.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY
from JumpScale9Lib.clients.rivine.types.signatures import Ed25519PublicKey
from JumpScale9Lib.clients.rivine.errors import DoubleSignatureError
from JumpScale9Lib.clients.rivine import utils
import ed25519
import pytest


def test_ssf_double_singature():
    """
    Tests that the SingleSignatureFulfillment type does not allow double singnatures
    """
    _, pk = ed25519.create_keypair(entropy=lambda x: b'a'*64)
    key = Ed25519PublicKey(pub_key=pk.to_bytes())
    ssf = SingleSignatureFulfillment(pub_key=key)
    ssf._signature = 'hello'
    with pytest.raises(DoubleSignatureError):
        ssf.sign(sig_ctx={})


def test_ssf_json():
    """
    Tests the json representation of SingleSignatureFulfillment
    """
    expected_output = {'type': 1,
                      'data': {
                            'publickey': 'ed25519:6161616161616161616161616161616161616161616161616161616161616161',
                            'signature': ''
                            }
                        }
    _, pk = ed25519.create_keypair(entropy=lambda x: b'a'*64)
    key = Ed25519PublicKey(pub_key=pk.to_bytes())
    ssf = SingleSignatureFulfillment(pub_key=key)
    assert ssf.json == expected_output, "Failed to generate the correct json representation of the SingleSignatureFulfillment"



def test_unlockhashcondition_binary():
    """
    Tests the generation of binary encoded version of unlockhashcondition object
    """
    expected_output = bytearray(b'\x01!\x00\x00\x00\x00\x00\x00\x00\x012M\xcf\x02}\xd4\xa3\n\x93,D\x1f6Z%\xe8k\x17=\xef\xa4\xb8\xe5\x89H%4q\xb8\x1br\xcf')
    hash = utils.hash(b'hello')
    ulh = UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
    ulhc = UnlockHashCondition(unlockhash=ulh)
    assert ulhc.binary == expected_output, "Failed to generate the expected binary value of unlockhashcondition"


def test_unlockhashcondition_json():
    """
    Tests the generation of json encoded version of the unlockhashcondition object
    """
    expected_output = {'type': 1,
                       'data': {
                                'unlockhash': '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a'
                                }
                        }
    hash = utils.hash(b'hello')
    ulh = UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
    ulhc = UnlockHashCondition(unlockhash=ulh)
    assert ulhc.json == expected_output, "Failed to generate the expected json value of unlockhashcondition"



def test_locktimecondition_binary():
    """
    Tests the generation of binary encoded version of LockTimeCondition object
    """
    expected_output = bytearray(b'\x03*\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x01\x012M\xcf\x02}\xd4\xa3\n\x93,D\x1f6Z%\xe8k\x17=\xef\xa4\xb8\xe5\x89H%4q\xb8\x1br\xcf')
    hash = utils.hash(b'hello')
    ulh = UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
    ulhc = UnlockHashCondition(unlockhash=ulh)
    ltc = LockTimeCondition(condition=ulhc, locktime=10)
    assert ltc.binary == expected_output, "Failed to generate the expected binary value of locktimecondition"


def test_locktimecondition_json():
    """
    Tests the generation of json encoded version of the LockTimeCondition object
    """
    expected_output = {'type': 3,
                       'data': {
                            'locktime': 10,
                            'condition': {
                                'type': 1,
                                'data': {
                                    'unlockhash': '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a'
                                    }
                                }
                            }
                        }

    hash = utils.hash(b'hello')
    ulh = UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
    ulhc = UnlockHashCondition(unlockhash=ulh)
    ltc = LockTimeCondition(condition=ulhc, locktime=10)
    assert ltc.json == expected_output, "Failed to generate the expected json value of locktimecondition"
