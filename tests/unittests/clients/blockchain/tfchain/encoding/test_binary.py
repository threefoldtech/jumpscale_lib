"""
Test module for binary encoding
"""

import pytest
from JumpscaleLib.clients.blockchain.tfchain.encoding import binary


def test_encode_int24():
    """
    Test encoding 24 bits integer
    """
    hex_str = '7af905'
    int_value = int.from_bytes(bytearray.fromhex(hex_str), byteorder='little')
    result = binary.IntegerBinaryEncoder.encode(int_value)
    assert hex_str == result.hex()


def test_encode_int_lower_bound_exception():
    with pytest.raises(binary.IntegerOutOfRange):
        binary.IntegerBinaryEncoder.encode(-1)


def test_encode_int_upper_bound_exception():
    with pytest.raises(binary.IntegerOutOfRange):
        binary.IntegerBinaryEncoder.encode(1 << 32)


def test_encode_slice():
    """
    Tests binary encoding of slices
    """
    test_cases = [
        {
            'value': [],
            'expected_result': bytearray(b'\x00')
        },
        {
            'value': [1, 2, 3],
            'expected_result': bytearray(b'\x06\x01\x02\x03')
        },
    ]

    for tc in test_cases:
        result = binary.SliceBinaryEncoder.encode(tc['value'])
        assert tc['expected_result'] == result


def test_encode_slice_length():
    """
    Tests encoding the slice length
    """
    test_cases = [
        # one byte
        {
            'value': 0,
            'expected_result': 1
        },
        {
            'value': 1,
            'expected_result': 1
        },
        {
            'value': 42,
            'expected_result': 1
        },
        {
            'value': (1 << 5),
            'expected_result': 1
        },
        {
            'value': (1 << 6),
            'expected_result': 1
        },
        # two bytes
        {
            'value': (1 << 7),
            'expected_result': 2
        },
        {
            'value': (1 << 8),
            'expected_result': 2
        },
        {
            'value': 15999,
            'expected_result': 2
        },
        {
            'value': (1 << 12),
            'expected_result': 2
        },
        {
            'value': (1 << 14)-1,
            'expected_result': 2
        },
        # three bytes
        {
            'value': (1 << 14),
            'expected_result': 3
        },
        {
            'value': (1 << 15),
            'expected_result': 3
        },
        {
            'value': 2000000,
            'expected_result': 3
        },
        {
            'value': (1 << 19),
            'expected_result': 3
        },
        {
            'value': (1 << 21)-1,
            'expected_result': 3
        },
        # four bytes
        {
            'value': (1 << 21),
            'expected_result': 4
        },
        {
            'value': (1 << 22),
            'expected_result': 4
        },
        {
            'value': (1 << 24),
            'expected_result': 4
        },
        {
            'value': (1 << 25),
            'expected_result': 4
        },
        {
            'value': (1 << 28)-1,
            'expected_result': 4
        },
        {
            'value': (1 << 29)-1,
            'expected_result': 4
        },
    ]

    for tc in test_cases:
        result = len(binary.SliceBinaryEncoder.encode_length(tc['value']))
        assert tc['expected_result'] == result


def test_encode_slice_length_exception():
    with pytest.raises(binary.SliceLengthOutOfRange):
        binary.SliceBinaryEncoder.encode_length(1 << 29)
