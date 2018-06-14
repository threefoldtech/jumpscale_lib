"""
Test module for RivineWallet js9 client
"""

from js9 import j
import time


from JumpScale9Lib.clients.rivine.types.transaction import TransactionFactory
txn = TransactionFactory.create_transaction(1)
# txn.add_data(bytearray('ot', encoding='utf-8'))
# txn.add_data(b'ot')
# txn.add_minerfee(100000000)
# print(txn.get_input_signature_hash(0).hex())
# raise RuntimeError('hello')


# use specific seed that has some funds
seed = 'siren own oil clean often undo castle sure creek squirrel group income size boost cart picture wing cram candy dutch congress actor taxi prosper'

client_data = {'bc_address': 'https://explorer.testnet.threefoldtoken.com/',
               'password_': 'test123',
               'minerfee': 100000000,
               'nr_keys_per_seed': 15,
               'seed_': seed}

rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
rivine_client.config.save()


# create a wallet based on the generated Seed
wallet = rivine_client.wallet

wallet.addresses


assert type(wallet._get_current_chain_height()) == int

address = '0145df536e9ad219fcfa9b2cd295d3499e59ced97e6cbed30d81373444db01acd563a402d9690c'
wallet._check_address(address=address)

#sync the wallet
wallet.current_balance
None

try:
    recipient = '01c90937f321837bf3d3e60c93e711a009f5735adae9a88491168a7059cbf4c11bcda0188e0a4c'
    data = b"Hello from Cairo!"
    transaction = wallet.send_money(amount=2, recipient=recipient, data=data, locktime=time.time() + 500)
    # transaction = wallet._create_transaction(amount=1000000000, recipient=recipient, sign_transaction=True, custom_data=data)
    # transaction = wallet._create_transaction(amount=2000000000, recipient=recipient,minerfee=100000000, sign_transaction=True, custom_data=data, locktime=time.time() + 300)

    # transaction = wallet.send_money(amount=2, recipient=recipient)
    print(transaction.json)
finally:
    import IPython
    IPython.embed()
