"""
Modules defines the unlockhash types
"""

UNLOCK_TYPE_PUBKEY = binaryarray([1])
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
    def __init__(unlock_type, hash):
        """
        Initialize new unlockhash

        @param unlock_type: The type of the unlock for this unlockhash, the client only support unlocktype 0x01 for public keys unlock type
        @param hash: Hashed value of the input lock
        """
