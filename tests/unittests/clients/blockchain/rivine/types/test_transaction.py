"""
Unittests for module JumpscaleLib.clients.blockchain.rivine.types.transaction
"""

from JumpscaleLib.clients.blockchain.rivine.types.transaction import \
    DEFAULT_TRANSACTION_VERSION, BOT_REGISTRATION_TRANSACTION_VERSION, BOT_RECORD_UPDATE_TRANSACTION_VERSION, \
    TransactionFactory, TransactionV1, \
    CoinInput, CoinOutput, _compute_monthly_bot_fees
from JumpscaleLib.clients.blockchain.rivine.types.unlockconditions import UnlockHashCondition, LockTimeCondition, SingleSignatureFulfillment
from JumpscaleLib.clients.blockchain.rivine.const import HASTINGS_TFT_VALUE
from unittest.mock import MagicMock
import json


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

"""
3Bot transaction tests
"""

def test_compute_monthly_bot_fees():
    testCases = {
        0: 0,
		1: 10,
		2: 20,
        8: 80,
        11: 110,
        12: 84,
        16: 112,
        24: 120,
        31: 155,
        32: 160,
        255: 1275,
    }
    for months, expectedFees in testCases.items():
        expectedFees *= HASTINGS_TFT_VALUE # in JS the oneCoin value is hardcoded (o.o)
        fees = _compute_monthly_bot_fees(months)
        assert fees == expectedFees

def test_transactionv144_load_dump_json():
    # load and dump a valid v144 tx from tfchain Go devnet
    json_input = '{"version":144,"data":{"names":["crazybot.foobar"],"nrofmonths":1,"txfee":"1000000000","coininputs":[{"parentid":"6678e3a75da2026da76753a60ac44f7e7737784015676b37cc2cdcf670dce2e5","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"cd07fbfd78be0edd1c9ca46bc18f91cde1ed05848083828c5d3848cd9671054527b630af72f7d95c0ddcd3a0f0c940eb8cfe4b085cb00efc8338b28f39155809"}}}],"refundcoinoutput":{"value":"99979897000000000","condition":{"type":1,"data":{"unlockhash":"017fda17489854109399aa8c1bfa6bdef40f93606744d95cc5055270d78b465e6acd263c96ab2b"}}},"identification":{"publickey":"ed25519:adc4090edbe28e3628f08a85d20b5055ea301cdb080d3b65a337a326e2e3556d","signature":"5211f813fb4e34ae348e2e746846bc72255512dc246ccafbb3bd3b916aac738bfe2737308d87cced4f9476be8715983cc6000e37f8e82e7b83f120776a358105"}}}'
    tx = TransactionFactory.from_json(json_input)
    assert tx.version == BOT_REGISTRATION_TRANSACTION_VERSION
    assert tx.json == json.loads(json_input)

def test_transactionv144_input_sig_hash():
    # load a valid v144 tx from tfchain Go devnet and create the input sig hash, ensure it is as expected
    json_input = '{"version":144,"data":{"names":["crazybot.foobar"],"nrofmonths":1,"txfee":"1000000000","coininputs":[{"parentid":"6678e3a75da2026da76753a60ac44f7e7737784015676b37cc2cdcf670dce2e5","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"cd07fbfd78be0edd1c9ca46bc18f91cde1ed05848083828c5d3848cd9671054527b630af72f7d95c0ddcd3a0f0c940eb8cfe4b085cb00efc8338b28f39155809"}}}],"refundcoinoutput":{"value":"99979897000000000","condition":{"type":1,"data":{"unlockhash":"017fda17489854109399aa8c1bfa6bdef40f93606744d95cc5055270d78b465e6acd263c96ab2b"}}},"identification":{"publickey":"ed25519:adc4090edbe28e3628f08a85d20b5055ea301cdb080d3b65a337a326e2e3556d","signature":"5211f813fb4e34ae348e2e746846bc72255512dc246ccafbb3bd3b916aac738bfe2737308d87cced4f9476be8715983cc6000e37f8e82e7b83f120776a358105"}}}'
    tx = TransactionFactory.from_json(json_input)
    assert tx.version == BOT_REGISTRATION_TRANSACTION_VERSION
    assert tx.get_input_signature_hash(0).hex() == 'b91b15b614b3c5c729a840542e4d6e7930a17fbd3245fe57f8cb1a9c59263637'

def test_transactionv145_load_dump_json():
    # load and dump a valid v145 tx from tfchain Go devnet
    json_input = '{"version":145,"data":{"id":3,"addresses":{"add":["example.com","127.0.0.1"],"remove":["example.org"]},"names":{"add":["giveme.yourfeedback","thisis.anexample"],"remove":["chatbot.example"]},"nrofmonths":4,"txfee":"1000000000","coininputs":[{"parentid":"81a0c1f3094b99b0858da8ebc95b52f2c3593ea399d7b72a66a930521aae61bb","fulfillment":{"type":1,"data":{"publickey":"ed25519:880ee50bd7efa4c8b2b5949688a09818a652727fd3c0cb406013be442df68b34","signature":"d612b679377298e6ccb8a877f7a129d34c65b8850cff1806b9f62d392b6ab173020c3698658275c748047642f8012a4ac75ea23e319bcc405c9d7f2b462b6a0b"}}}],"refundcoinoutput":{"value":"99998737000000000","condition":{"type":1,"data":{"unlockhash":"01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"}}},"signature":"f76e7ed808a9efe405804109d5e3c8695daf8b9bc7abf1e471fef94b3c4d36789b460f9e45cdf27d83d270b0836fef56bd499e1be8e1f279d367e961bbe62f03"}}'
    tx = TransactionFactory.from_json(json_input)
    assert tx.version == BOT_RECORD_UPDATE_TRANSACTION_VERSION
    assert tx.json == json.loads(json_input)

def test_transactionv145_input_sig_hash():
    # load a valid v145 tx from tfchain Go devnet and create the input sig hash, ensure it is as expected
    json_input = '{"version":145,"data":{"id":3,"addresses":{"add":["example.com","127.0.0.1"],"remove":["example.org"]},"names":{"add":["giveme.yourfeedback","thisis.anexample"],"remove":["chatbot.example"]},"nrofmonths":4,"txfee":"1000000000","coininputs":[{"parentid":"81a0c1f3094b99b0858da8ebc95b52f2c3593ea399d7b72a66a930521aae61bb","fulfillment":{"type":1,"data":{"publickey":"ed25519:880ee50bd7efa4c8b2b5949688a09818a652727fd3c0cb406013be442df68b34","signature":"d612b679377298e6ccb8a877f7a129d34c65b8850cff1806b9f62d392b6ab173020c3698658275c748047642f8012a4ac75ea23e319bcc405c9d7f2b462b6a0b"}}}],"refundcoinoutput":{"value":"99998737000000000","condition":{"type":1,"data":{"unlockhash":"01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"}}},"signature":"f76e7ed808a9efe405804109d5e3c8695daf8b9bc7abf1e471fef94b3c4d36789b460f9e45cdf27d83d270b0836fef56bd499e1be8e1f279d367e961bbe62f03"}}'
    tx = TransactionFactory.from_json(json_input)
    assert tx.version == BOT_RECORD_UPDATE_TRANSACTION_VERSION
    assert tx.get_input_signature_hash(0).hex() == 'af3293da1e441b6c832a0763e17bb5b516bbb78540509a3418cd08253e584cf0'
