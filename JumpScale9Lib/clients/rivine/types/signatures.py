"""
This modules defines types related to signatures
"""

from JumpScale9Lib.clients.rivine.encoding import binary

SIGEd25519 = 'ed25519'
SPECIFIER_SIZE = 16
NON_SIA_SPECIFIER = 'NonSia'

class SiaPublicKey:
    """
    A SiaPublicKey is a public key prefixed by a Specifier. The Specifier
	indicates the algorithm used for signing and verification.
    """
    def __init__(self, algorithm, pub_key):
        """
        Initialize new SiaPublicKey
        """
        self.algorithm = algorithm
        self.pub_key = pub_key

    @property
    def binary(self):
        """
        Encodes the public key into binary format
        """
        key_value = bytearray()
        s = bytearray(SPECIFIER_SIZE)
        s[:len(self.algorithm] = bytearray(self.algorithm, encoding='utf-8')
        key_value.extend(s)
        key_value.extend(binary.encode(self.pub_key, type='slice'))
        return key_value
        

class Ed25519PublicKey(SiaPublicKey):
    """
    Ed25519PublicKey returns pk as a SiaPublicKey, denoting its algorithm as Ed25519.
    """
    def __init__(self, pub_key):
        """
        Initialize new Ed25519PublicKey
        """
        self.algorithm = SIGEd25519
        super().__init__(pub_key=pub_key)
