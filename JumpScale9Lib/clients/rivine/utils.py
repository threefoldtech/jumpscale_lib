"""
Modules for common utilites
"""

from pyblake2 import blake2b

# from .const import ADDRESS_TYPE_SIZE, WALLET_ADDRESS_TYPE, HASH_SIZE
from .const import HASH_SIZE
from JumpScale9Lib.clients.rivine.encoding import binary
# from .errors import InvalidUnlockHashChecksumError
# from JumpScale9Lib.clients.rivine.types.unlockhash import UNLOCKHASH_SIZE, UNLOCKHASH_CHECKSUM_SIZE

def hash(data, encoding_type=None):
    """
    Hashes the input binary input data usinng the blake2b algorithm and

    @param data: Input data to be hashed
    @param encoding_type: Type of the data to guide the binary encoding before hashing
    @returns: Hashed value of the input data
    """
    binary_data = binary.encode(data, type_=encoding_type)
    return blake2b(binary_data, digest_size=HASH_SIZE).digest()

#
# def get_unlockhash_from_address(address):
#     """
#     Construct an unlock hash [32]byte array from an address
#     """
#     indexes = (ADDRESS_TYPE_SIZE, UNLOCKHASH_SIZE*2 + ADDRESS_TYPE_SIZE)
#     _, key_hex, sum_hex = address[:indexes[0]], address[indexes[0]:indexes[1]], address[indexes[1]:]
#     unlockhash_bytes = bytearray.fromhex(key_hex)
#     sum_bytes = bytearray.fromhex(sum_hex)
#     expected_checksum = blake2b(WALLET_ADDRESS_TYPE + unlockhash_bytes, digest_size=UNLOCKHASH_SIZE).digest()
#     if sum_bytes != expected_checksum[:UNLOCKHASH_CHECKSUM_SIZE]:
#         raise InvalidUnlockHashChecksumError("Cannot decode address to unlockhash")
#     return key_hex
