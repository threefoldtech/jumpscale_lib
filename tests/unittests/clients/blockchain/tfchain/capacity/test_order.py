"""
Test module for the capacity order class
"""

import pytest
from JumpscaleLib.clients.blockchain.tfchain.capacity import order

def test_binary_encoding_capacity_order():
    def create_co(cru, mru, hru, sru, nru, duration, description):
        co = order.CapacityOrder()
        co.cru = cru
        co.mru = mru
        co.hru = hru
        co.sru = sru
        co.nru = nru
        co.duration = duration
        co.description = description
        return co

    test_cases = {
        bytes([0, 1, 0, 0]): create_co(0, 0, 0, 0, 0, 1, bytearray()),
        bytes([8, 2, 0, 1, 0, 0]): create_co(0, 0, 0, 0, 2, 1, bytearray()),
        bytes([24, 3, 0, 0, 0, 2, 0, 1, 0, 0]): create_co(0, 0, 0, 3, 2, 1, bytearray()),
        bytes([56, 4, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 0]): create_co(0, 0, 4, 3, 2, 1, bytearray()),
        bytes([120, 5, 0, 4, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 0]): create_co(0, 5, 4, 3, 2, 1, bytearray()),
        bytes([248, 6, 5, 0, 4, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 0]): create_co(6, 5, 4, 3, 2, 1, bytearray()),
        bytes([0, 1, 0, 2, 4, 2]): create_co(0, 0, 0, 0, 0, 1, bytearray([4, 2])),
        bytes([8, 2, 0, 1, 0, 3, 1, 2, 3]): create_co(0, 0, 0, 0, 2, 1, bytearray([1, 2, 3])),
        bytes([24, 3, 0, 0, 0, 2, 0, 1, 0, 1, 1]): create_co(0, 0, 0, 3, 2, 1, bytearray([1])),
        bytes([56, 4, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 2, 4, 2]): create_co(0, 0, 4, 3, 2, 1, bytearray([4, 2])),
        bytes([120, 5, 0, 4, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 4, 2, 0, 0, 3]): create_co(0, 5, 4, 3, 2, 1, bytearray([2, 0, 0, 3])),
        bytes([248, 6, 5, 0, 4, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 2, 4, 2]): create_co(6, 5, 4, 3, 2, 1, bytearray([4, 2])),
    }
    for b, expected_result in test_cases.items():
        # assert we can correctly binary decode
        result = order.CapacityOrder.from_binary(b)
        assert expected_result == result
        # assert we can correctly binary encode
        result_b = result.binary()
        assert b == result_b