"""
Test module for RivineWallet js9 client
"""

from js9 import j
from JumpScale9Lib.clients.rivine.RivineWallet import RivineWallet, SpendableKey


# use specific seed that has some funds
seed = 'siren own oil clean often undo castle sure creek squirrel group income size boost cart picture wing cram candy dutch congress actor taxi prosper'

client_data = {'bc_address': 'https://explorer.testnet.threefoldtoken.com/',
               'password_': 'test123',
               'minerfee': 10,
               'nr_keys_per_seed': 10,
               'seed_': seed}

rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
rivine_client.config.save()

expected_unlockhashes = ['fa8ee5ecf2551f9a5a8cdc338ad6ef781d53929d712ebbe25b93a1ff4c89584d6a430fd60874',
 '3e47b15d4a1d3974a326556cd127d5b86d607cb8726165bb4c9a3515a98b2ba1982a35939c7f',
 '573cbb732e4a075c3b95103efce8dbc479cc79d2ac9ad917c0c1f5facfbfa6648366a0735080',
 'f65988eefa5f76d0d73f9879e91772e709faa947d1d6f03a2e36b554698594bf07738072f6bb',
 '1c0baae330902503bbdaa945be3d8f6359c0f21bdba392046c7507992aa900ba0df185208b15',
 '27ac47fda7f5ac7f3eeb83a29e26aeb9f82d14dd9b74d7ec277af90d2f90d8b97f8ca7b9f4a9',
 '45df536e9ad219fcfa9b2cd295d3499e59ced97e6cbed30d81373444db01acd586e8f302d602',
 '62c3980953d55d7670859f474aec7a8caeb1517421c0e744a6c7c8e4ad00a6db043c35d0c0e6',
 'dd6b2cb6098f301d6928041d58119c5c9cc62be4a6ba797c8f8a510cd3b0c5bd38bec968e62b',
 '9d0e215e29a548bb3aca345eeffe7a47d4bb49e7ecae29d5bd548632b1829559c283fe00bf6c']

# create a wallet based on the generated Seed
# rivine_wallet = RivineWallet(seed=seed, bc_network='http://185.69.166.13:2015', nr_keys_per_seed=5)
rivine_wallet = rivine_client.wallet

actual_unlockhashes = rivine_wallet.addresses

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


address = '20f4c5d518839b61a2a704bd45d47e25a319df75c1fa18c01856440079d34b0b0181076ce5c2'
actual_address_info = rivine_wallet.check_address(address=address)
assert actual_address_info == expected_address_info, "Expected address info is not the same as check_address found"


#sync the wallet
rivine_wallet.sync_wallet()

# create transaction
recipient = '01e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1'
transaction = rivine_wallet.create_transaction(amount=500, recipient=recipient)


print('Transaction created!')

rivine_wallet.commit_transaction(transaction)
print('Transaction pushed to chain')

# create transaction with custom data
custom_data = bytearray("hello from Dresden", encoding='utf-8')

transaction = rivine_wallet.create_transaction(amount=500, recipient=recipient, custom_data=custom_data)

rivine_wallet.commit_transaction(transaction)
print('Transaction pushed to chain')
