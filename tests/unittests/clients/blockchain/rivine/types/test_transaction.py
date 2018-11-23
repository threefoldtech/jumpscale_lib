"""
Unittests for module JumpscaleLib.clients.blockchain.rivine.types.transaction
"""

from JumpscaleLib.clients.blockchain.rivine.types.transaction import \
    DEFAULT_TRANSACTION_VERSION, BOT_REGISTRATION_TRANSACTION_VERSION, BOT_RECORD_UPDATE_TRANSACTION_VERSION, \
    TransactionFactory, TransactionV1, \
    CoinOutputSummary, TransactionSummary, \
    CoinInput, CoinOutput, _compute_monthly_bot_fees
from JumpscaleLib.clients.blockchain.rivine.types.unlockconditions import UnlockHashCondition, LockTimeCondition, SingleSignatureFulfillment
from JumpscaleLib.clients.blockchain.rivine.const import HASTINGS_TFT_VALUE
from unittest.mock import MagicMock
import json
import secrets


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
summary tx types tests,
summary types are used to return blockchain data to the user
in a user-friendly way, where the details are abstracted or hidden
"""

def __create_cos(amount, locked, addresses, signatures):
    v = CoinOutputSummary()
    v._amount = amount
    v._locked = locked
    v._addresses = addresses
    v._signatures_required = signatures
    # raw_condition is assigned when executing the test case
    return v

def test_coin_output_summary():
    test_cases = {
        # nil condition and time-locked nil-conditioned outputs
        '{"value":"42", "condition":{}}': __create_cos(42, 0, ['0'*78], 1),
        '{"value":"123", "condition":{"type":3,"data":{"locktime":1542791301}}}': __create_cos(123, 1542791301, ['0'*78], 1),
        '{"value":"123", "condition":{"type":3,"data":{"locktime":1542791301, "condition":{}}}}': __create_cos(123, 1542791301, ['0'*78], 1),
        '{"value":"123", "condition":{"type":3,"data":{"locktime":1542791301, "condition":{"type": 0}}}}': __create_cos(123, 1542791301, ['0'*78], 1),
        '{"value":"123", "condition":{"type":3,"data":{"locktime":1542791200}}}': __create_cos(123, 1542791200, ['0'*78], 1),
        # single-signature/multi-signature, optionally time-locked outputs
        '{"value":"100000000000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}': __create_cos(100000000000000000, 0, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f'], 1),
        '{"value":"100000000000000000","condition":{"type":4,"data":{"unlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f","01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f"],"minimumsignaturecount":10}}}': __create_cos(100000000000000000, 0, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f','01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f'], 10),
        '{"value":"100000000000000000","condition":{"type":3, "data":{"locktime":2,"condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}}}': __create_cos(100000000000000000, 2, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f'], 1),
        '{"value":"100000000000000000","condition":{"type":3, "data":{"locktime":4,"condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}}}': __create_cos(100000000000000000, 4, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f'], 1),
        '{"value":"100000000000000000","condition":{"type":3, "data":{"locktime":1,"condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}}}': __create_cos(100000000000000000, 1, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f'], 1),
        '{"value":"100000000000000000","condition":{"type":3, "data":{"locktime":2,"condition":{"type":4,"data":{"unlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f","01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f"],"minimumsignaturecount":2}}}}}': __create_cos(100000000000000000, 2, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f','01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f'], 2),
        '{"value":"100000000000000000","condition":{"type":3, "data":{"locktime":4,"condition":{"type":4,"data":{"unlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f","01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f"],"minimumsignaturecount":3}}}}}': __create_cos(100000000000000000, 4, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f','01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f'], 3),
        '{"value":"100000000000000000","condition":{"type":3, "data":{"locktime":1,"condition":{"type":4,"data":{"unlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f","01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f"],"minimumsignaturecount":4}}}}}': __create_cos(100000000000000000, 1, ['015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f','01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f'], 4),
        # atomic swap condition (v2) is ignored
        '{"value":"1000000000000","condition":{"type":2,"data":{"sender":"01822fd5fefd2748972ea828a5c56044dec9a2b2275229ce5b212f926cd52fba015846451e4e46","receiver":"01c56890b1b31ec8dbfe87c6829096c12839ae31bb62f1b10d9dacd4947df8e25bb5ff2ba13f4d","hashedsecret":"66028cc407a168b39ae7b538e8b4b25f0d945e18e32c502a1f3bc6ff3b71ca37","timelock":1542965902}}}': __create_cos(1000000000000, 0, [], 0),
        # output with unknown condition
        '{"value":"1", "condition":{"type":1000}}': __create_cos(1, 0, [], 0),
    }
    for json_output, expected_summary in test_cases.items():
        raw_output = json.loads(json_output)
        expected_summary._raw_condition = raw_output.get('condition', {})
        summary = CoinOutputSummary.from_raw_coin_output(raw_output)
        assert expected_summary == summary

def __create_ts(inputs, outputs, description):
    v = TransactionSummary()
    v._coin_inputs = inputs
    v._coin_outputs = outputs
    v._description = description
    # id still has to be assigned
    return v

def test_transaction_summary():
    test_cases = {
        # regular tx with no coin outputs
        '{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"bf69bcf666e17fbfdbb298c82d77e499b075ef11d9ec4408dd001e5833b1267a","fulfillment":{"type":1,"data":{"publickey":"ed25519:97d784b93d5769d2df0010b793622eae14a33992b958e8406cceb827a8101d29","signature":"86949eb390054150ea5b6f14e09ced9087ec2db9a00b837b23ff65f8093b805cc9e0f7cac57d1011851c8bc4b1cc051f825e41a5d3909c7e4ffa3232b149b906"}}}],"blockstakeoutputs":[{"value":"1000","condition":{"type":1,"data":{"unlockhash":"0195de96da59de0bd59c416e96d17df1a5bbc80acb6b02a1db0cde0bcdffca55a4f7f369e955ef"}}}],"minerfees":null}}': __create_ts([], [], ''),
        # most common tx, a single coin output
        '{"version":1,"data":{"coininputs":[{"parentid":"dee5559ef1bb0467ddbc5199bb1daa718394e9cd259f062ca94cb41e6fb3d2e6","fulfillment":{"type":1,"data":{"publickey":"ed25519:ae86cb853e747459b832e9c8327b0cb477d5b28808bde6943dd83e91a894d9b5","signature":"f566aed8d638a9906aebc3e2ada4df06cf3294e4f63127d5297f07180faf565933242199da28a6003700da5ea0facd1ede7dec600bfd6f48dfd4d1fdb589ac03"}}}],"coinoutputs":[{"value":"2000000000000","condition":{"type":1,"data":{"unlockhash":"01de789caf18b2de08e4d0256529aa1bc2d2fd7487d5dff02832cea39007d272cbff1feeb57282"}}},{"value":"99995623000000000","condition":{"type":1,"data":{"unlockhash":"01cc962a280afd4d6e73aab298f7ff64ab29a61a90bb873b625fd63ff5939a5edafc83270c1969"}}}],"minerfees":["1000000000"]}}': __create_ts(['dee5559ef1bb0467ddbc5199bb1daa718394e9cd259f062ca94cb41e6fb3d2e6'], [__create_cos(2000000000000, 0, ['01de789caf18b2de08e4d0256529aa1bc2d2fd7487d5dff02832cea39007d272cbff1feeb57282'], 1), __create_cos(99995623000000000, 0, ['01cc962a280afd4d6e73aab298f7ff64ab29a61a90bb873b625fd63ff5939a5edafc83270c1969'], 1)], ''),
        # a common tx, with a single coin output AND a description (filled in as arbitrary data)
        '{"version":1,"data":{"coininputs":[{"parentid":"fafede06beb869023e1962afc948d6c592bed1f4bb072fae8c5c228bbd76eab3","fulfillment":{"type":1,"data":{"publickey":"ed25519:cdf05a944cf11b654ac30c92ecba7f126f4f92647bdc60ac126c30d2c6d22023","signature":"d207a9324ca3a54df31c33cb55615ee9c7ba557ed1a029732ab03395aa4bfe9f4550f8dfca449241af0b02ac0306f19f57120f23cd954c267ad39dc6eff97604"}}}],"coinoutputs":[{"value":"100000000000","condition":{"type":1,"data":{"unlockhash":"0191dee035d25bf008817309d14e972651cc515b09dadde3155357682da120886f96133186a9f3"}}},{"value":"99995196000000000","condition":{"type":1,"data":{"unlockhash":"019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c"}}}],"minerfees":["1000000000"],"arbitrarydata":"dGVzdCBkYXRh"}}': __create_ts(['fafede06beb869023e1962afc948d6c592bed1f4bb072fae8c5c228bbd76eab3'], [__create_cos(100000000000, 0, ['0191dee035d25bf008817309d14e972651cc515b09dadde3155357682da120886f96133186a9f3'], 1), __create_cos(99995196000000000, 0, ['019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c'], 1)], 'test data'),
        # a regular tx with multiple outputs
        '{"version":1,"data":{"coininputs":[{"parentid":"0fb6bec427a3bd717b0f89790153fb01ee9d3b5cd01f4f30996be05640b595d7","fulfillment":{"type":1,"data":{"publickey":"ed25519:29eb219e2a943325c2ce4bad26e464e24c9eed50f3b5acdd8a772e0947a0db4f","signature":"12f2499bb55b4782e2edaacad724dbbde2c8b58d14e060f3b42eb2d16765d72f068c2c759e5f42646d1e1e7b7e4e2625046e1558cd3ed8d5b166c431622a410f"}}}],"coinoutputs":[{"value":"100000000000","condition":{}},{"value":"123000000000","condition":{"type":3,"data":{"locktime":2,"condition":{}}}},{"value":"1000000000","condition":{"type":3,"data":{"locktime":1542791301,"condition":{"type":1,"data":{"unlockhash":"01de789caf18b2de08e4d0256529aa1bc2d2fd7487d5dff02832cea39007d272cbff1feeb57282"}}}}},{"value":"99995398000000000","condition":{"type":1,"data":{"unlockhash":"01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936"}}}],"minerfees":["1000000000"]}}': __create_ts(['0fb6bec427a3bd717b0f89790153fb01ee9d3b5cd01f4f30996be05640b595d7'], [__create_cos(100000000000, 0, ['0'*78], 1), __create_cos(123000000000, 2, ['0'*78], 1), __create_cos(1000000000, 1542791301, ['01de789caf18b2de08e4d0256529aa1bc2d2fd7487d5dff02832cea39007d272cbff1feeb57282'], 1), __create_cos(99995398000000000, 0, ['01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936'], 1)], ''),
        # a minter definition transaction
        '{"version":128,"data":{"nonce":"3iLQbzi5wwo=","mintfulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"1ce1d534ff508784628f28080cdbcedd93c4a68efc70f90342eed6bfb75713ed872c2ecc776720dd430cd061389226f6ab67a2cd32b67ebd09998a461f2a1000"}},"mintcondition":{"type":1,"data":{"unlockhash":"01589f71e02fbc86f47f0b7d7a087e8868075c879332830a0c1ab9b4fb6ed629ebb1835bf0d2b3"}},"minerfees":["1000000000"]}}': __create_ts([], [], ''),
        # a coin creation transaction
        '{"version":129,"data":{"nonce":"ggzIoHFQRlo=","mintfulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"11ce90b62b9082db48c5dc2122d9b8778d810c4e27a11dc38e5be8c177cf6d6e9dcc4c25a4068adf9a7c14a5782b19c109dd8d41850c3650ed7184c56f929404"}},"coinoutputs":[{"value":"100000000000","condition":{"type":1,"data":{"unlockhash":"0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6"}}}],"minerfees":["1000000000"]}}': __create_ts([], [__create_cos(100000000000, 0, ['0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6'], 1)], ''),
        # a 3Bot registration transaction
        '{"version":144,"data":{"addresses":["91.198.174.192","example.org"],"names":["chatbot.example"],"nrofmonths":1,"txfee":"1000000000","coininputs":[{"parentid":"a3c8f44d64c0636018a929d2caeec09fb9698bfdcbfa3a8225585a51e09ee563","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"909a7df820ec3cee1c99bd2c297b938f830da891439ef7d78452e29efb0c7e593683274c356f72d3b627c2954a24b2bc2276fed47b24cd62816c540c88f13d05"}}}],"refundcoinoutput":{"value":"99999899000000000","condition":{"type":1,"data":{"unlockhash":"01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f"}}},"identification":{"publickey":"ed25519:00bde9571b30e1742c41fcca8c730183402d967df5b17b5f4ced22c677806614","signature":"98e71668dfe7726a357039d7c0e871b6c0ca8fa49dc1fcdccb5f23f5f0a5cab95cfcfd72a9fd2c5045ba899ecb0207ff01125a0151f3e35e3c6e13a7538b340a"}}}': __create_ts(['a3c8f44d64c0636018a929d2caeec09fb9698bfdcbfa3a8225585a51e09ee563'], [__create_cos(99999899000000000, 0, ['01b49da2ff193f46ee0fc684d7a6121a8b8e324144dffc7327471a4da79f1730960edcb2ce737f'], 1)], ''), # TODO: handle also 3Bot Payout Fee
        # a 3Bot record update transaction
        '{"version":145,"data":{"id":1,"addresses":{"add":["127.0.0.1"],"remove":["example.org"]},"names":{"add":["another.sexyname"],"remove":["chatbot.example"]},"nrofmonths":5,"txfee":"1000000000","coininputs":[{"parentid":"b5de97d299b1fa931eeeedf5e73cb435ff2545353cb2d004d597d2ef1261c106","fulfillment":{"type":1,"data":{"publickey":"ed25519:a271b9d4c1258f070e1e8d95250e6d29f683649829c2227564edd5ddeb75819d","signature":"70fa1b7002138ca7d3c5b16e321ff5d12fb1e8a58f03aeff1a2b61b877ad7c4be6f8da55fc4b7710c5e21d79bc8550caea574159e9795c172482793818da6e0d"}}}],"refundcoinoutput":{"value":"99999778000000000","condition":{"type":1,"data":{"unlockhash":"01370af706b547dd4e562a047e6265d7e7750771f9bff633b1a12dbd59b11712c6ef65edb1690d"}}},"signature":"b751f135686c0db4a0399d3fedcb4b312eb77b2f6c2e5e4af6a357d481d3e5408cb7a6137e1e1b84a2f79b3d890331f223e4b663c221642a44b2ca223126a70d"}}': __create_ts(['b5de97d299b1fa931eeeedf5e73cb435ff2545353cb2d004d597d2ef1261c106'], [__create_cos(99999778000000000, 0, ['01370af706b547dd4e562a047e6265d7e7750771f9bff633b1a12dbd59b11712c6ef65edb1690d'], 1)], ''), # TODO: handle also 3Bot Payout Fee
        # a 3Bot name transfer transaction
        '{"version":146,"data":{"sender":{"id":1,"signature":"73525655dd4598951834451b85d93ff4e5d6cc7c02fe5e56b87c82ad17d843327e31875cbb217aea135d824fe8a265172f083c3129367d8450b90b67b37ecc00"},"receiver":{"id":2,"signature":"5baf5978ce505323cbdd14161a6eeb6e00714f590c7286dfba499e9503df89f6987e85330bcae1fe12aeb01742d4f7b28135e00d11b2869cc2cc08297306a308"},"names":["another.sexyname"],"txfee":"1000000000","coininputs":[{"parentid":"8a2e93f840a9290f9d63f47e1509b369d2c139e8ae51cff3aebc20b0637d831b","fulfillment":{"type":1,"data":{"publickey":"ed25519:41e84f3b0f6a06dd7e45ded4d0e227869725355b73906b82d9e3ffc0b6b01416","signature":"3087dcc59e2e8c9f0608ef7a2e7c7de499b4962e622732407819c0e4c5714f864ca53f26aca87dcbccf058751bd3512165f67ce3314a1edc614381d77a370d0e"}}}],"refundcoinoutput":{"value":"99999626000000000","condition":{"type":1,"data":{"unlockhash":"0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55"}}}}}': __create_ts(['8a2e93f840a9290f9d63f47e1509b369d2c139e8ae51cff3aebc20b0637d831b'], [__create_cos(99999626000000000, 0, ['0186cea43fa0d303a6379ae76dd79f014698956fb982751549e3ff3844b23fa9551c1725470f55'], 1)], ''), # TODO: handle also 3Bot Payout Fee
    }
    for json_tx, expected_summary in test_cases.items():
        expected_summary._id = secrets.token_hex(64)
        raw_tx = json.loads(json_tx)
        index = 0
        coin_outputs = raw_tx.get('data', {}).get('coinoutputs', [])
        refund_output = raw_tx.get('data', {}).get('refundcoinoutput', {})
        if refund_output: # TODO handle this better, what a mess these 3Bot transactions
            coin_outputs.append(refund_output)
        for coin_output in coin_outputs:
            expected_summary._coin_outputs[index]._raw_condition = coin_output.get('condition', {})
            index += 1
        summary = TransactionSummary.from_raw_transaction(expected_summary._id, False, raw_tx)
        assert expected_summary == summary

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
