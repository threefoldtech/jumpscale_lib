"""
Test module for RivineWallet js9 client
"""

from js9 import j
import time


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


assert type(wallet.get_current_chain_height()) == int

address = '0145df536e9ad219fcfa9b2cd295d3499e59ced97e6cbed30d81373444db01acd563a402d9690c'
wallet.check_address(address=address)

#sync the wallet
wallet.current_balance


try:
    recipient = '01fffda0a9b5d6494af38294028cac4401768f30740271d8314d486ebf3585647eece15d5f8b47'
    data = b'hello from cairo'
    # transaction = wallet.send_money(amount=2, recipient=recipient, data=data)
    # transaction = wallet._create_transaction(amount=1000000000, recipient=recipient, sign_transaction=True, custom_data=data)
    transaction = wallet._create_transaction(amount=2000000000, recipient=recipient, sign_transaction=True)
    # transaction = wallet.send_money(amount=2, recipient=recipient)
    print(transaction.json)
finally:
    import IPython
    IPython.embed()
