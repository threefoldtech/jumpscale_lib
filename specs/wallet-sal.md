# Wallet SAL

```python
# generate seeds
seed = j.clients.blockchain.rivine.generate_seed()
client_data = {'seed_': seed, 'bc_address': 'https://explorer.testnet.threefoldtoken.com/','nr_keys_per_seed': 10, 'minerfee': 10}
# get rivine client
rivine_client = j.clients.blockchain.rivine.get('mytestwallet', data=client_data)
rivine_client.config.save()
# get your wallet this is based on the seeds so each time you provide the same seed you will get the same wallet
wallet = rivine_client.wallet 
wallet.check_ballance() # check current balance
# send money to someones address
transaction = wallet.spend_money(amount=500, recipient=recipient)
# commit the transaction
transaction.commit(transaction)
# get you wallet addresses
addresses = wallet.addresses