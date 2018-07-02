"""
Modules for common utilites
"""

from pyblake2 import blake2b
from .const import HASH_SIZE
from JumpScale9Lib.clients.rivine.encoding import binary

def hash(data, encoding_type=None):
    """
    Hashes the input binary data using the blake2b algorithm

    @param data: Input data to be hashed
    @param encoding_type: Type of the data to guide the binary encoding before hashing
    @returns: Hashed value of the input data
    """
    binary_data = binary.encode(data, type_=encoding_type)
    return blake2b(binary_data, digest_size=HASH_SIZE).digest()
