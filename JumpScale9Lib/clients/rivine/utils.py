"""
Modules for common utilites
"""

from pyblake2 import blake2b

from .const import ADDRESS_TYPE_SIZE, UNLOCKHASH_SIZE, UNLOCKHASH_CHECKSUM_SIZE
from .errors import InvalidUnlockHashChecksumError

def big_int_to_binary(big_int):
    """
    Convert a big integer value to a binary array

    @param big_int: Integer to convert
    """
    result = bytearray()
    nbytes, rem = divmod(big_int.bit_length(), 8)
    if rem:
        nbytes += 1
    result.extend(int_to_binary(nbytes))
    result.extend(big_int.to_bytes(nbytes, byteorder='big'))
    return result


def int_to_binary(value):
    """
    Convert an int to a binary format
    """
    return value.to_bytes(8, byteorder='little')


def get_unlockhash_from_address(address):
    """
    Construct an unlock hash [32]byte array from an address
    """
    indexes = (ADDRESS_TYPE_SIZE, UNLOCKHASH_SIZE*2 + ADDRESS_TYPE_SIZE)
    _, key_hex, sum_hex = address[:indexes[0]], address[indexes[0]:indexes[1]], address[indexes[1]:]
    unlockhash_bytes = bytearray.fromhex(key_hex)
    sum_bytes = bytearray.fromhex(sum_hex)
    expected_checksum = blake2b(unlockhash_bytes, digest_size=UNLOCKHASH_SIZE).digest()
    if sum_bytes != expected_checksum[:UNLOCKHASH_CHECKSUM_SIZE]:
        raise InvalidUnlockHashChecksumError("Cannot decode address to unlockhash")
    return key_hex
