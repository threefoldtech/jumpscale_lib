"""
Modules defines the unlockhash types
"""

from pyblake2 import blake2b
from JumpScale9Lib.clients.rivine import utils

UNLOCK_TYPE_PUBKEY = bytearray([1])
UNLOCKHASH_SIZE = 32
UNLOCKHASH_TYPE = 'unlockhash'
UNLOCKHASH_SIZE = 32
UNLOCKHASH_CHECKSUM_SIZE = 6

class UnlockHash:
    """
    An UnlockHash is a specially constructed hash of the UnlockConditions type.
	"Locked" values can be unlocked by providing the UnlockConditions that hash
	to a given UnlockHash. See SpendConditions.UnlockHash for details on how the
	UnlockHash is constructed.
	UnlockHash struct {
		Type UnlockType
		Hash crypto.Hash
	}
    """
    def __init__(self, unlock_type, hash):
        """
        Initialize new unlockhash

        @param unlock_type: The type of the unlock for this unlockhash, the client only support unlocktype 0x01 for public keys unlock type
        @param hash: Hashed value of the input lock
        """
        self._unlock_type = unlock_type
        self._hash = hash


    def __str__(self):
        """
        String representation of UnlockHash object
        """
        uh_checksum = utils.hash([self._unlock_type, self._hash])
        return '{}{}{}'.format(self._unlock_type.hex(), self._hash.hex(), uh_checksum[:UNLOCKHASH_CHECKSUM_SIZE].hex())


    def __repr__(self):
        """
        Calls __str__
        """
        return str(self)
