"""
Unittests for rivine binary encoding module
"""

import pytest
from unittest.mock import MagicMock, patch
import JumpScale9Lib.clients.rivine.encoding.binary
from JumpScale9Lib.clients.rivine.encoding import binary


def test_encode_all():
    """
    Test encode_all function
    """
    with patch.object(JumpScale9Lib.clients.rivine.encoding.binary, "encode") as encode_mock:
        result = binary.encode_all(['hello', 15])
        assert encode_mock.call_count == 2
        assert type(result) == bytearray


def test_encode_None():
    """
    Test encode None value
    """
    # test encoding None values
    result = binary.encode(None)
    assert len(result) == 0, "Wrong length of bytearray after encoding None value"
    assert type(result) == bytearray, "Wrong type after encoding None value"


def test_encode_unknown_type():
    """
    Test encode unknown data type
    """
    with pytest.raises(ValueError):
        binary.encode('hello', type_='not supported type')

def test_encode_hex():
    """
    Test encode hex values
    """
    value = b'hello world'
    output = binary.encode(value.hex(), type_='hex')
    assert output == value, "Failed to encode hex value to binary"


def test_encode_binary():
    """
    Test encode binary values
    """
    value = b'hello world'
    output = binary.encode(value)
    assert output == value, "Failed to encode binary value to binary"


def test_encode_int():
    """
    Test encode int values
    """
    value = 15
    output = binary.encode(value)
    expected_output = b'\x0f\x00\x00\x00\x00\x00\x00\x00'
    assert output == expected_output, "Failed to encode integer value to binary"


def test_encode_bool():
    """
    Test encode bool values
    """
    value = True
    output = binary.encode(value)
    expected_output = bytearray(b'\x01')
    assert output == expected_output, "Failed to encode boolean value to binary"


def test_encode_list():
    """
    Test encode list values
    """
    value = [15, True]
    output = binary.encode(value)
    expected_output = bytearray(b'\x0f\x00\x00\x00\x00\x00\x00\x00\x01')
    assert output == expected_output, "Failed to encode list value to binary"


def test_encode_object():
    """
    Test encode custom object that implement the binary property
    """
    expected_output = b'custom object here'
    class CustomObj:
        @property
        def binary(self):
            return expected_output

    output = binary.encode(CustomObj())
    assert output == expected_output, "Failed to encode custom value to binary"


def test_encode_currency():
    """
    Test encode currency values
    """
    value = 15000000000000000
    expected_output = bytearray(b'\x07\x00\x00\x00\x00\x00\x00\x005Jk\xa7\xa1\x80\x00')
    output = binary.encode(value, type_='currency')
    assert output == expected_output, "Failed to encode currency value to binary"


def test_encode_slice():
    """
    Test encode slice values
    """
    value = [15, True]
    expected_output = bytearray(b'\x02\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x01')
    output = binary.encode(value, type_='slice')
    assert output == expected_output, "Failed to encode slice value to binary"


def test_decode_int():
    """
    Test decode integers from binary
    """
    value = bytearray([1])
    output = binary.decode(value, type_=int)
    assert output == 1, "Failed to decode integer value from binary"
