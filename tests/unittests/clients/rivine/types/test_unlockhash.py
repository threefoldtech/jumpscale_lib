"""
Unittests for JumpscaleJumpscaleLib.clients.rivine.types.unlockhash module
"""

from JumpscaleLib.clients.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY
from JumpscaleLib.clients.rivine import utils

def test_unlock_to_string(ulh):
    """
    Tests the string representation of an unlockhash
    """
    expected_output = '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a'
    assert str(ulh) == expected_output, "String representation of unlockhash is not correct"


def test_unlockhash_binary(ulh):
    """
    Tests the binary representation of an unlockhash
    """
    expected_output = bytearray(b'\x012M\xcf\x02}\xd4\xa3\n\x93,D\x1f6Z%\xe8k\x17=\xef\xa4\xb8\xe5\x89H%4q\xb8\x1br\xcf')
    assert ulh.binary == expected_output, "Binary representation of unlockhash is not correct"

def test_unlockhash_from_string():
    """
    Tests loading an unlockhash from a string
    """
    input = '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a'
    assert str(UnlockHash.from_string(input)) == input, "Failed to load unlockhash from string"
