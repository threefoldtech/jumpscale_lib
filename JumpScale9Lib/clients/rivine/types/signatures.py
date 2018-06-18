"""
This modules defines types related to signatures
"""

from JumpScale9Lib.clients.rivine.encoding import binary

SIGEd25519 = 'ed25519'
SPECIFIER_SIZE = 16

class SiaPublicKey:
    """
    A SiaPublicKey is a public key prefixed by a Specifier. The Specifier
	indicates the algorithm used for signing and verification.
    """
    def __init__(self, algorithm, pub_key):
        """
        Initialize new SiaPublicKey
        """
        self._algorithm = algorithm
        self._pub_key = pub_key

    @property
    def binary(self):
        """
        Encodes the public key into binary format
        """
        key_value = bytearray()
        s = bytearray(SPECIFIER_SIZE)
        s[:len(self._algorithm)] = bytearray(self._algorithm, encoding='utf-8')
        key_value.extend(s)
        key_value.extend(binary.encode(self._pub_key, type_='slice'))
        return key_value


    @property
    def json(self):
        """
        Returns a json encoded version of the SiaPublicKey
        """
        return "{}:{}".format(self._algorithm, self._pub_key.hex())


class Ed25519PublicKey(SiaPublicKey):
    """
    Ed25519PublicKey returns pk as a SiaPublicKey, denoting its algorithm as Ed25519.
    """
    def __init__(self, pub_key):
        """
        Initialize new Ed25519PublicKey
        """
        super().__init__(algorithm=SIGEd25519, pub_key=pub_key)
