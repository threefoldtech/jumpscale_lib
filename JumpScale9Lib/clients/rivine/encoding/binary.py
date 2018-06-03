"""
Binary encoder module
This module implements methods to encode values from different data types to binary format that conform with the algorithm used in Rivine protocol
https://github.com/rivine/rivine/blob/master/doc/transactions/transaction.md#binary-encoding
"""

def encode(value, type_=None):
    """
    Encode the value into its binary representation
    """
    result = bytearray()
    if value is None:
        return result
    if type_ == 'slice':
        # slice is a variable size array, which means we need to prefix the size of the array and then we can encode the list itself
        result.extend(encode(len(value)))
        for item in value:
            result.extend(encode(item))
    elif type_ == 'currency':
        nbytes, rem = divmod(value.bit_length(), 8)
        if rem:
            nbytes += 1
        result.extend(encode(nbytes))
        result.extend(value.to_bytes(nbytes, byteorder='big'))
    elif type_ is None:
        # try to figure out the type of the value
        value_type = type(value)
        if value_type in (bytes, bytearray):
            result.extend(value)
        elif value_type is int:
            result = value.to_bytes(8, byteorder='little')
        elif value_type is bool:
            result = bytearray([1]) if value else bytearray([0])
        else:
            if hasattr(value, 'binary'):
                result.extend(value.binary)

    return result
