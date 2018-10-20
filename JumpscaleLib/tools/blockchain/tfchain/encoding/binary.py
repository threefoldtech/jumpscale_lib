"""
Moudle to support binary encoding for tfchain
"""

from JumpscaleLib.clients.blockchain.rivine import encoding

SUPPORTED_TYPES = ['slice', 'int8', 'uint8',
                    'int16', 'uint16', 'int24',
                    'uint24', 'int32', 'uint32',
                    'int64', 'uint64', 'int',
                    'uint']

class BinaryEncoder:
    """
    Support binary encoding for tfchain
    """
    @staticmethod
    def encode(value, type_=None):
        """
        Enocdes a value to its binary representation

        @param value: Value to be encoded
        @param type_: Type of the value, if not given, the type will be detected automatically
        """

        if type_ not in SUPPORTED_TYPES:
            # then we delegate to the rivine library implementation
            return encoding.binary.encode(value, type_)
        
        if 'int' in type_:
            return IntegerBinaryEncoder.encode(value, type_)
        elif type_ == 'slice':
            return SliceBinaryEncoder.encode(value)


class SliceBinaryEncoder:
    """
    Support binary encoding for slice type
    Slice is an array with no pre-defined size
    """
    @staticmethod
    def encode(value):
        """
        Encodes a slice to a binary

        @param value: Value to be encoded        
        """
        

class IntegerBinaryEncoder:
    """
    Support binary encoding for integers
    """
    @staticmethod
    def encode(value, type_):
        """
        Encodes an integer value to binary

        @param value: Value to be encoded
        @param type_: Type of the value, if not given, the type will be detected automatically
        """
        # strip the uint from the type_ string and calculate 
        # required number of bytes
        type_ = type_.strip('uint')
        if type_ == '':
            nr_of_bytes = 8
        else:
            nr_of_bytes = int(int(type_) / 8)
        return value.to_bytes(nr_of_bytes, byteorder='little')
        

            
