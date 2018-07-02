"""
Unittests for module JumpScale9Lib.clients.rivine.types.unlockconditions
"""

from JumpScale9Lib.clients.rivine.types.unlockconditions import UnlockHashCondition, LockTimeCondition, SingleSignatureFulfillment
from JumpScale9Lib.clients.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY
from JumpScale9Lib.clients.rivine.types.signatures import Ed25519PublicKey
from JumpScale9Lib.clients.rivine.errors import DoubleSignatureError
from JumpScale9Lib.clients.rivine import utils
from unittest.mock import MagicMock
import ed25519
import pytest




def test_ssf_sign(ed25519_key, spendable_key):
    """
    Tests sing the method of SingleSignatureFulfillment
    """
    expected_output = b'Y\xcf5rp\xc5\xf5\xd2\xc2\xeay\xcag\x8d\xb7GB\x7f\x81l\xfa.\xfd\x9aQV\xf2#V&\xb4\x00G\xa3\xd0\xaf\x9bBQ\x02=\xe9\xb7\xcc\x8e\xbaYv"\xd8\x97\x0ec\x01/%\x02_\xa2\xe9\x07\x98:\x04'
    ssf = SingleSignatureFulfillment(pub_key=ed25519_key)
    sig_ctx = {
        'input_idx': 0,
        'secret_key': spendable_key.secret_key,
        'transaction': MagicMock(),
    }
    sig_ctx['transaction'].get_input_signature_hash = MagicMock(return_value=bytes('hello', encoding='utf-8'))
    ssf.sign(sig_ctx=sig_ctx)
    assert ssf._signature == expected_output


def test_ssf_double_singature(ed25519_key):
    """
    Tests that the SingleSignatureFulfillment type does not allow double singnatures
    """
    ssf = SingleSignatureFulfillment(pub_key=ed25519_key)
    ssf._signature = 'hello'
    with pytest.raises(DoubleSignatureError):
        ssf.sign(sig_ctx={})


def test_ssf_json(ed25519_key):
    """
    Tests the json representation of SingleSignatureFulfillment
    """
    expected_output = {'type': 1,
                      'data': {
                            'publickey': 'ed25519:6161616161616161616161616161616161616161616161616161616161616161',
                            'signature': ''
                            }
                        }
    ssf = SingleSignatureFulfillment(pub_key=ed25519_key)
    assert ssf.json == expected_output, "Failed to generate the correct json representation of the SingleSignatureFulfillment"



def test_unlockhashcondition_binary(ulh):
    """
    Tests the generation of binary encoded version of unlockhashcondition object
    """
    expected_output = bytearray(b'\x01!\x00\x00\x00\x00\x00\x00\x00\x012M\xcf\x02}\xd4\xa3\n\x93,D\x1f6Z%\xe8k\x17=\xef\xa4\xb8\xe5\x89H%4q\xb8\x1br\xcf')
    ulhc = UnlockHashCondition(unlockhash=ulh)
    assert ulhc.binary == expected_output, "Failed to generate the expected binary value of unlockhashcondition"


def test_unlockhashcondition_json(ulh):
    """
    Tests the generation of json encoded version of the unlockhashcondition object
    """
    expected_output = {'type': 1,
                       'data': {
                                'unlockhash': '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a'
                                }
                        }
    ulhc = UnlockHashCondition(unlockhash=ulh)
    assert ulhc.json == expected_output, "Failed to generate the expected json value of unlockhashcondition"



def test_locktimecondition_binary(ulh):
    """
    Tests the generation of binary encoded version of LockTimeCondition object
    """
    expected_output = bytearray(b'\x03*\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x01\x012M\xcf\x02}\xd4\xa3\n\x93,D\x1f6Z%\xe8k\x17=\xef\xa4\xb8\xe5\x89H%4q\xb8\x1br\xcf')
    ulhc = UnlockHashCondition(unlockhash=ulh)
    ltc = LockTimeCondition(condition=ulhc, locktime=10)
    assert ltc.binary == expected_output, "Failed to generate the expected binary value of locktimecondition"


def test_locktimecondition_json(ulh):
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

    ulhc = UnlockHashCondition(unlockhash=ulh)
    ltc = LockTimeCondition(condition=ulhc, locktime=10)
    assert ltc.json == expected_output, "Failed to generate the expected json value of locktimecondition"
