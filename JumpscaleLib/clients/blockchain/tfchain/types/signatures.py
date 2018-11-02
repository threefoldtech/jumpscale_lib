"""
This modules defines types related to signatures
"""

from JumpscaleLib.clients.blockchain.tfchain.encoding import binary
from JumpscaleLib.clients.blockchain.rivine.types import signatures

from enum import IntEnum

class InvalidSiaPublicKeySpecifier(Exception):
    """
    InvalidSiaPublicKeySpecifier error
    """

class SiaPublicKeySpecifier(IntEnum):
    NIL = 0
    ED25519 = 1

    @classmethod
    def from_string(cls, algo_str):
        if not algo_str:
            return SiaPublicKeySpecifier.NIL
        if algo_str == signatures.SIGEd25519:
            return SiaPublicKeySpecifier.ED25519
        raise InvalidSiaPublicKeySpecifier("{} is an invalid Sia Public Key specifier".format(algo_str))

    def to_string(self):
        if self == SiaPublicKeySpecifier.ED25519:
            return signatures.SIGEd25519
        return ""

    @property
    def binary(self):
        """
        Encodes the public key specifier into binary format
        """
        return binary.IntegerBinaryEncoder.encode(self)

class SiaPublicKey:
    """
    A SiaPublicKey is a public key prefixed by a Specifier. The Specifier
	indicates the algorithm used for signing and verification.
    """

    @classmethod
    def from_string(cls, pub_key_str):
        """
        Creates a SiaPublicKey from a string
        """
        algo, pub_key = pub_key_str.split(':')
        return cls(algorithm=SiaPublicKeySpecifier.from_string(algo), pub_key=bytearray.fromhex(pub_key))

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
        key_value.extend(binary.IntegerBinaryEncoder.encode(self._algorithm))
        key_value.extend(self._pub_key)
        return key_value
    
    def to_string(self):
        return "{}:{}".format(self._algorithm.to_string(), self._pub_key.hex())

    @property
    def json(self):
        """
        Returns a json encoded version of the SiaPublicKey
        """
        return self.to_string()

