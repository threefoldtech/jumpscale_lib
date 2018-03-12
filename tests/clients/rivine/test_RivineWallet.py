"""
Test module for RivineWallet js9 client
"""

from js9 import j
from mnemonic import Mnemonic
from JumpScale9Lib.clients.rivine.RivineWallet import RivineWallet, SpendableKey

# create a random seed
m = Mnemonic('english')
seed = m.generate()

# use specific seed that has some funds
seed = 'siren own oil clean often undo castle sure creek squirrel group income size boost cart picture wing cram candy dutch congress actor taxi prosper'

client_data = {'bc_address': 'http://185.69.166.13:2015',
               'password_': 'test123',
               'minerfee': 10,
               'nr_keys_per_seed': 5,
               'seed_': seed}

rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
rivine_client.config.save()

expected_unlockhashes = ['20f4c5d518839b61a2a704bd45d47e25a319df75c1fa18c01856440079d34b0b0181076ce5c2',
 'ddd9d661b8694b1e7b36c09c211aeb400579c3ca9feff4d86d892c84fe8b10f31cae805c23e2',
 '59012f7b5a1529ce0ec0bcf641cc65da2f2cb2d8fa65b7f6b57653e9053488a9ec8057930d76',
 '0d59ae725d13d8db337dd1356c736a24aab00f8e6d64ae324516d0fd0ff00ed8ef597789cfcc',
 '87a97bb7aac48ed7f3ea857536368a68b11c227cd5fc374c3a3f5df999d1d726f2623fe5e82b']

# create a wallet based on the generated Seed
# rivine_wallet = RivineWallet(seed=seed, bc_network='http://185.69.166.13:2015', nr_keys_per_seed=5)
rivine_wallet = rivine_client.wallet

actual_unlockhashes = [key for key in rivine_wallet.keys.keys()]

assert set(expected_unlockhashes) == set(
    actual_unlockhashes), "Unlockhashes do not match"

assert type(rivine_wallet.get_current_chain_height()) == int


expected_address_info =\
{'block': {'arbitrarydatacount': 0,
  'blockid': '0000000000000000000000000000000000000000000000000000000000000000',
  'blockstakeinputcount': 0,
  'blockstakeoutputcount': 0,
  'coininputcount': 0,
  'coinoutputcount': 0,
  'difficulty': '0',
  'estimatedactivebs': '0',
  'height': 0,
  'maturitytimestamp': 0,
  'minerfeecount': 0,
  'minerpayoutcount': 0,
  'minerpayoutids': None,
  'rawblock': {'minerpayouts': None,
   'parentid': '0000000000000000000000000000000000000000000000000000000000000000',
   'pobsindexes': {'BlockHeight': 0, 'OutputIndex': 0, 'TransactionIndex': 0},
   'timestamp': 0,
   'transactions': None},
  'target': [0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0],
  'totalcoins': '0',
  'transactioncount': 0,
  'transactions': None,
  'transactionsignaturecount': 0},
 'blocks': None,
 'hashtype': 'unlockhash',
 'transaction': {'blockstakeinputoutputs': None,
  'blockstakeoutputids': None,
  'coininputoutputs': None,
  'coinoutputids': None,
  'height': 0,
  'id': '0000000000000000000000000000000000000000000000000000000000000000',
  'parent': '0000000000000000000000000000000000000000000000000000000000000000',
  'rawtransaction': {'arbitrarydata': None,
   'blockstakeinputs': None,
   'blockstakeoutputs': None,
   'coininputs': None,
   'coinoutputs': None,
   'minerfees': None,
   'transactionsignatures': None}},
 'transactions': [{'blockstakeinputoutputs': None,
   'blockstakeoutputids': None,
   'coininputoutputs': [{'unlockhash': 'a4f19051f863e7ae0a03f91bbf55daa70182009ab345c15dcf253c9f64b18dcb64bb6e579704',
     'value': '98999997000000000000000000000000'}],
   'coinoutputids': ['7bf659ef8b67d7584eb3951f18b5ff15a22f6f827b917c8f3cb1a156472980ad',
    'b7e412be3cf4636d4d65056d270f8c0097679b4dd3ffe355fbbc0ca57eb20a8c'],
   'height': 2377,
   'id': '47a7933971055f77fc81201f8627637f7c96e25add4000235b23233d297d1bc9',
   'parent': '41f31717a15c6ac7f4bfbcb2b82f4bb53b3e46ebf25eb86ddc024ef5eb053ea3',
   'rawtransaction': {'arbitrarydata': None,
    'blockstakeinputs': None,
    'blockstakeoutputs': None,
    'coininputs': [{'parentid': '4d255b370019da2bd2b01140dd0c3c2c38587f4fad660e21ef329cfe6af8f84b',
      'unlockconditions': {'publickeys': [{'algorithm': 'ed25519',
         'key': 'JRaHaz1pybO9kbSw/TKHirxg0kZHvMMf0LQgRl9ALS0='}],
       'signaturesrequired': 1,
       'timelock': 0}}],
    'coinoutputs': [{'unlockhash': '4b5d72161354051a70a8e0d81cc3577993a22079ffec8e83d18161efb7bb1970c7d22e463169',
      'value': '98989996000000000000000000000000'},
     {'unlockhash': '20f4c5d518839b61a2a704bd45d47e25a319df75c1fa18c01856440079d34b0b0181076ce5c2',
      'value': '10000000000000000000000000000'}],
    'minerfees': ['1000000000000000000000000'],
    'transactionsignatures': [{'coveredfields': {'arbitrarydata': None,
       'blockstakeinputs': None,
       'blockstakeoutputs': None,
       'coininputs': None,
       'coinoutputs': None,
       'minerfees': None,
       'transactionsignatures': None,
       'wholetransaction': True},
      'parentid': '4d255b370019da2bd2b01140dd0c3c2c38587f4fad660e21ef329cfe6af8f84b',
      'publickeyindex': 0,
      'signature': '641ZU6EX1Q40TyAACb+V/FBysza+cd+1DmOavQAkfTbLOEZWR25ePUuU1HEnHGyndEvJUXp4FTgcfa7dk23fAg==',
      'timelock': 0}]}}]}

# import json
# expected_address_info = json.loads(str(expected_address_info))
address = '20f4c5d518839b61a2a704bd45d47e25a319df75c1fa18c01856440079d34b0b0181076ce5c2'
actual_address_info = rivine_wallet.check_address(address=address)
# import pdb; pdb.set_trace()
assert actual_address_info == expected_address_info, "Expected address info is not the same as check_address found"


# import copy
# original_keys = copy.deepcopy(rivine_wallet._keys)
# override the keys attribute in the wallet to use our testing address
# rivine_wallet._keys = {address: SpendableKey(m.to_seed(seed))}
# after overriding the keys attributes we can try to sync the wallet
rivine_wallet.sync_wallet()

expected_unspent_coins_outputs = {'b7e412be3cf4636d4d65056d270f8c0097679b4dd3ffe355fbbc0ca57eb20a8c': {'unlockhash': '20f4c5d518839b61a2a704bd45d47e25a319df75c1fa18c01856440079d34b0b0181076ce5c2',
  'value': '10000000000000000000000000000'}}

assert expected_unspent_coins_outputs == rivine_wallet.unspent_coins_outputs, "Unexpected unspent coins outputs"


# set back the original keys
# import pdb; pdb.set_trace()
# rivine_wallet._keys = original_keys
recipient = 'e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1'
# transacton = rivine_wallet.create_transaction(amount=10, recipient=recipient)
transaction = rivine_wallet.create_transaction(amount=500, recipient=recipient)

expected_transaction_json = {'arbitrarydata': '',
 'blockstakeinputs': '',
 'blockstakeoutputs': '',
 'coininputs': [{'parentid': 'b7e412be3cf4636d4d65056d270f8c0097679b4dd3ffe355fbbc0ca57eb20a8c',
   'unlockconditions': {'publickeys': [{'algorithm': 'Ed25519',
      'key': 'qdsbI+5eEQwM/9QzBwdP7TDESR2syXRQ2jhAhyx1hPA='}],
    'signaturesrequired': 1,
    'timelock': 0}}],
 'coinoutputs': [{'unlockhash': 'e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1',
   'value': '500'},
  {'unlockhash': 'ddd9d661b8694b1e7b36c09c211aeb400579c3ca9feff4d86d892c84fe8b10f31cae805c23e2',
   'value': '9999999999999999999999999490'}],
 'minerfees': ['10'],
 'transactionsignatures': [{'coveredfields': {'arbitrarydata': '',
    'blockstakeinputs': '',
    'blockstakeoutputs': '',
    'coininputs': '',
    'coinoutputs': '',
    'minerfees': '',
    'transactionsignatures': '',
    'wholetransaction': True},
   'parentid': 'b7e412be3cf4636d4d65056d270f8c0097679b4dd3ffe355fbbc0ca57eb20a8c',
   'publickeyindex': 0,
   'signature': 'EDqeePftyr/d0QF1OGI4AHk1sHe+ynfGnR1V0OZR+xui/SO0EYHVXbaVZ8QV5NElaNuQ1XHoA8S/rIL/vTBPBA==',
   'timelock': 0}]}

assert transaction.json == expected_transaction_json, "Wrong transaction json was generated"
print('Transaction created!')