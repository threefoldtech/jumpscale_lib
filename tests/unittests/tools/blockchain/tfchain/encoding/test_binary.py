"""
Test module for binary encoding
"""

import pytest
from JumpscaleLib.tools.blockchain.tfchain.encoding import binary


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
    
