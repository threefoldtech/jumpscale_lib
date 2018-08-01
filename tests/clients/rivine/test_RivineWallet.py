"""
Test module for RivineWallet jumpscale client
"""

from jumpscale import j
import time


from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory
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

try:
    recipient = '01b1e730f6c8d8ef0615c05e87075265cf27b929a20767e3e652b6d303e95205bdd61fdfb88925'
    data = b"Hello from Cairo!"
    # transaction = wallet.send_money(amount=2, recipient=recipient, data=data, locktime=time.time() + 500)
    current_height = wallet._get_current_chain_height()
    # wallet.send_money(amount=2, recipient='01b1e730f6c8d8ef0615c05e87075265cf27b929a20767e3e652b6d303e95205bdd61fdfb88925', locktime=current_height + 5)
    # transaction = wallet._create_transaction(amount=1000000000, recipient=recipient, sign_transaction=True, custom_data=data)
    transaction = wallet._create_transaction(amount=2000000000, recipient=recipient,minerfee=100000000, sign_transaction=True, custom_data=data, locktime=current_height + 5)

    # transaction = wallet.send_money(amount=2, recipient=recipient)
    print(transaction.json)
finally:
    import IPython
    IPython.embed()
