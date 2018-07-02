"""
Unittests for module JumpScale9Lib.clients.rivine.types.transaction
"""

from JumpScale9Lib.clients.rivine.types.transaction import DEFAULT_TRANSACTION_VERSION, TransactionFactory, TransactionV1, CoinInput, CoinOutput

def test_create_transaction_v1():
    """
    Tests creating a V1 transaction
    """
    assert type(TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)) == TransactionV1, "Wrong type transaction created"


def test_coininput_json():
    """
    Tests the json output of CoinInput
    """
