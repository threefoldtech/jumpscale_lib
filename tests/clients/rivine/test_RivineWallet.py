"""
Test module for RivineWallet js9 client
"""

from js9 import j


# use specific seed that has some funds
seed = 'siren own oil clean often undo castle sure creek squirrel group income size boost cart picture wing cram candy dutch congress actor taxi prosper'

client_data = {'bc_address': 'https://explorer.testnet.threefoldtoken.com/',
               'password_': 'test123',
               'minerfee': 100000000,
               'nr_keys_per_seed': 10,
               'seed_': seed}

rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
rivine_client.config.save()

expected_unlockhashes = ['012bdb563a4b3b630ddf32f1fde8d97466376a67c0bc9a278c2fa8c8bd760d4dcb4b9564cdea6f',
                         '01b81f9e02d6be3a7de8440365a7c799e07dedf2ccba26fd5476c304e036b87c1ab716558ce816',
                         '01253b501da49528ff760675a95c0b71e02579425270723476b2798cc7a219870feccb6b15c8a0',
                         '019c03f961a03fb10f56aee2f3ee83c7c1c5669c141caf9db2c1c60ecebc1e49fff4c2553a5285',
                         '016da14f2ebd6bed12c93ca04308d34652ba34a9d93ae50dd6282f2ef1b2b6b17e3012704554b0',
                         '0166358d9c0efc3fca196df46e8b985e9fc0696e0b5b10d8d5d84eddeddbcc4b6ad60bf95fcb70',
                         '0117ffb7b036cb81ad230da98e74fe8b06bbdcea5880a99ffa249f45825abe2faed53cc656c26b',
                         '015069f937c810fff0266c08b49f5cb26ff92207e30051a8d0107909e7014ed4f2c7f7d1ad311d',
                         '0167bb3ab263a1a69c3d7f098738f5aa6ab5e26334c1bfade941f1ddaf868c4c7230f609c78eef',
                         '01e2a7a3ec862a80756caa81d0f33b619b48144b1e85d6997a249157affa4f0dac73231378ff14']

# create a wallet based on the generated Seed
rivine_wallet = rivine_client.wallet

actual_unlockhashes = rivine_wallet.addresses

assert set(expected_unlockhashes) == set(
    actual_unlockhashes), "Unlockhashes do not match"

assert type(rivine_wallet.get_current_chain_height()) == int

address = '0145df536e9ad219fcfa9b2cd295d3499e59ced97e6cbed30d81373444db01acd563a402d9690c'
rivine_wallet.check_address(address=address)

#sync the wallet
rivine_wallet.current_balance


try:
    recipient = '0112a7c1813746c5f6d5d496441d7a6a226984a3cc318021ee82b5695e4470f160c6ca61f66df2'
    data = b'hello from cairo'
    transaction = rivine_wallet.send_money(amount=2, recipient=recipient, data=data)
    # transaction = rivine_wallet._create_transaction(amount=1000000000, recipient=recipient, sign_transaction=True, custom_data=data)
    print(transaction.json)
finally:
    import IPython
    IPython.embed()
