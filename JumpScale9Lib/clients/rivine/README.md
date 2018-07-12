# JumpScale Client for Rivine

The client work as a lightweight wallet for the Rivine blockchain network.
It supports the following functionalities:

- Starting from a seed, be able to derive the public and private keypairs.
- Use the public keys to create wallet addresses.
- These addresses can be used to query the explorer to get the coininputs
- Remove those that are already spent
- When creating the transaction, select the coin inputs to have equal or more coins than the required output + minerfee. Change can be written back to one of your own addresses. Note that an input must be consumed in its entirety.
- For every public key in the input, the corresponding private key is required to sign the transaction to be valid


# How to use
Starting from a seed which can be a sentence of [12, 15, 18, 21, 24] words, for more information about the seed please check: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

You can generate new seed by using the following commands in your js9 shell
```python
        j.data.encryption.mnemonic.generate(256)
```

Alternativly, you can generate a seed from the client factory
```python
seed = j.clients.rivine.generate_seed()
```

From a seed you can create new wallet
```python
        from JumpScale9Lib.clients.rivine.RivineWallet import RivineWallet
        wallet = RivineWallet(seed=seed,
                                    bc_network='https://explorer.testnet.threefoldtoken.com/',
                                    bc_network_password='test123',
                                    nr_keys_per_seed=5,
                                    minerfee=100000000)
        # where seed is the seed you have or generated
        # bc_network: is the url to the blockchain network explorer node
        # bc_network_password: is the password to use while communicating with the chain explorer node
        # nr_keys_per_seed: is how many keys to generate per seed
        # minerfee: How many hastings should be added as minerfee
```

Or alternatively you can configure the jumpscale client instance using the following code:
```python
    client_data = {'bc_address': 'https://explorer.testnet.threefoldtoken.com/',
'password_': 'test123',
 'minerfee': 10,
 'nr_keys_per_seed': 5,
 'seed_': 'festival mobile negative nest valid cheese pulp alpha relax language friend vast'}

    rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
    rivine_client.config.save()
    wallet = rivine_client.wallet
```

After creating the wallet you can check your wallet balance
```python
        wallet.current_balance
```

You should see something similar to the following output
```bash
Out[2]: 16.7
```

You can check the addresses of in your wallet
```python
wallet.addresses
```

After checking your balance, you can starting sending money if you have enough funds in your wallet
```python
    recipient = '01e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1'
    transaction = wallet.send_money(amount=2, recipient=recipient)
```

You can also create transactions with custom data
```python
# create transaction with custom data
recipient = '01e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1'
custom_data = b"hello from Dresden"
transaction = wallet.send_money(amount=2, recipient=recipient, data=data)
```

You can also add a locktime to your transactions
```python
import time
recipient = '01e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1'
custom_data = b"hello from Dresden"
# 15 minutes locktime
locktime = time.time() + 900
transaction = wallet.send_money(amount=2, recipient=recipient, data=data, locktime=locktime)
```

## How to use AtomicSwap
The light wallet client supports the different atomicswap operations. It allows the user to:
- Initiate a new atomicswap contract
- Participate in an exsisting atomicswap contract
- Validate the information of an atomicswap contract
- Withdraw funds from atomicswap contract
- Refund funds from atomicswap contract

For more details about the atomicswap process, it is recommended to check the documentation at the Rivine offical repository here: https://github.com/rivine/rivine/blob/master/doc/atomicswap/atomicswap.md

The light wallet client exposes the APIs via the following hook:
```python
wallet.atomicswap.[TAB]
```
