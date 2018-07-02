"""
Unittests for module JumpScale9Lib.clients.rivine.types.transaction
"""

from JumpScale9Lib.clients.rivine.types.transaction import DEFAULT_TRANSACTION_VERSION, TransactionFactory, TransactionV1, CoinInput, CoinOutput
from JumpScale9Lib.clients.rivine.types.unlockconditions import UnlockHashCondition, LockTimeCondition, SingleSignatureFulfillment
from unittest.mock import MagicMock


def test_create_transaction_v1():
    """
    Tests creating a V1 transaction
    """
    assert type(TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)) == TransactionV1, "Wrong type transaction created"


def test_coininput_json(ed25519_key, ulh):
    """
    Tests the json output of CoinInput
    """
    expected_output = {'parentid': '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a',
     'fulfillment': {'type': 1,
      'data': {'publickey': 'ed25519:6161616161616161616161616161616161616161616161616161616161616161',
       'signature': ''}}}
    ssf = SingleSignatureFulfillment(pub_key=ed25519_key)
    parent_id = str(ulh)
    ci = CoinInput(parent_id=parent_id, fulfillment=ssf)
    assert ci.json == expected_output


def test_coininput_sign(ed25519_key, ulh):
    """
    Tests siging a CoinInput
    """
    ssf = SingleSignatureFulfillment(pub_key=ed25519_key)
    ssf.sign = MagicMock()
    parent_id = str(ulh)
    ci = CoinInput(parent_id=parent_id, fulfillment=ssf)
    sig_ctx = {
        'input_idx': 0,
        'secret_key': None,
        'transaction': None,
    }
    ci.sign(input_idx=sig_ctx['input_idx'],
            transaction=sig_ctx['transaction'],
            secret_key=sig_ctx['secret_key'])
    assert ssf.sign.called_once_with(sig_ctx)


def test_coinoutput_binary(ulh):
    """
    Tests the binary output of a CoinOuput
    """
    expected_output = bytearray(b'\x02\x00\x00\x00\x00\x00\x00\x00\x01\xf4\x01!\x00\x00\x00\x00\x00\x00\x00\x012M\xcf\x02}\xd4\xa3\n\x93,D\x1f6Z%\xe8k\x17=\xef\xa4\xb8\xe5\x89H%4q\xb8\x1br\xcf')
    ulhc = UnlockHashCondition(unlockhash=ulh)
    co = CoinOutput(value=500, condition=ulhc)
    assert co.binary == expected_output

def test_coinoutput_json(ulh):
    """
    Tests the json output of a CoinOuput
    """
    expected_output = {'value': '500', 'condition': {'type': 1, 'data': {'unlockhash': '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a'}}}
    ulhc = UnlockHashCondition(unlockhash=ulh)
    co = CoinOutput(value=500, condition=ulhc)
    assert co.json == expected_output


def test_transactionv1_json(recipient, ulh, spendable_key):
    """
    Tests the json output of the v1 transaction
    """
    expected_output = {'version': 1, 'data': {'coininputs': [{'parentid': '01324dcf027dd4a30a932c441f365a25e86b173defa4b8e58948253471b81b72cf57a828ea336a', 'fulfillment': {'type': 1, 'data': {'publickey': 'ed25519:6161616161616161616161616161616161616161616161616161616161616161', 'signature': ''}}}], 'coinoutputs': [{'value': '500', 'condition': {'type': 1, 'data': {'unlockhash': '01479db781aae5ecbcc2331b7996b0d362ae7359b3fe25dcacdbf62926db506cbd3edf8bd46077'}}}], 'minerfees': ['100']}}
    txn = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)
    txn.add_coin_input(parent_id=str(ulh), pub_key=spendable_key.public_key)
    txn.add_coin_output(value=500, recipient=recipient)
    txn.add_minerfee(100)
    assert txn.json == expected_output


def test_transactionv1_get_input_signature_hash(recipient, ulh, spendable_key):
    """
    Tests generating signature hash of a transaction input
    """
    expected_output = b'#0@HW`X\x99c\x11\xf8\x08#\x15\x1a\x00\xe7e\xdb\xbf\x98e\xd1\xa7\xba\x94@\xd6\x1f\x1e\xc2/'
    txn = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)
    txn.add_coin_input(parent_id=str(ulh), pub_key=spendable_key.public_key)
    txn.add_coin_output(value=500, recipient=recipient)
    txn.add_minerfee(100)
    assert txn.get_input_signature_hash(0) == expected_output
