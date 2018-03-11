# JumpScale Client for Rivine

The client work as a lightweight wallet for the Rivine blockchain network.
It supports the following functionalities:

- Starting from a seed, be able to derive the public and private keypairs.
- Use the public keys to create unlockcondition objects, which can be hashed to get the addresses.
- These addresses can be used to query the explorer to get the coininputs
- Remove those that are already spent
- When creating the transaction, select the coin inputs to have equal or more coins than the required output + minerfee. Change can be written back to one of your own addresses. Note that an input must be consumed in its entirety.
- For every public key in the input, the corresponding private key is required to sign the transaction to be valid


## Dependecies
The client uses the world list proposed in BIP-0039 and depends on the library provided them: https://github.com/trezor/python-mnemonic (pip install git+https://github.com/trezor/python-mnemonic.git)
To generate keypairs we depend on the ed25519 python implementation here: https://github.com/warner/python-ed25519 (pip install ed25519)

To generate UnlockHashes, we use merkletree implementation from here: https://github.com/Tierion/pymerkletools (pip install merkletools) 

# How to use
Starting from a seed which can be a sentence of [12, 15, 18, 21, 24] words, for more information about the seed please check: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

You can generate new seed by using the following commands in your js9 shell
```python
        from mnemonic import Mnemonic
        m = Mnemonic('english')
        seed = m.generate(strength=256)
```

From a seed you can create new wallet
```python
        from JumpScale9Lib.clients.rivine.RivineWallet import RivineWallet
        rivine_wallet = RivineWallet(seed=seed, 
                                    bc_network='http://185.69.166.13:2015',
                                    bc_network_password='test123',
                                    nr_keys_per_seed=5,
                                    minerfee=10)
        # where seed is the seed you have or generated
        # bc_network: is the url to the blockchain network explorer node
        # bc_network_password: is the password to use while communicating with the chain explorer node
        # nr_keys_per_seed: is how many keys to generate per seed
        # minerfee: How many hastings should be added as minerfee
```

Or alternatively you can configure the jumpscale client instance using the following code:
```python
    client_data = {'bc_address': 'http://185.69.166.13:2015',
'password_': 'test123',
 'minerfee': 10,
 'nr_keys_per_seed': 5,
 'seed_': 'festival mobile negative nest valid cheese pulp alpha relax language friend vast'}

    rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
    rivine_client.config.save()
    rivine_wallet = rivine_client.wallet
``` 

After creating the wallet you can sync the wallet with the blockchain network (this will not build a full node locally)
```python
        rivine_wallet.sync_wallet()
```

You should see something similar to the following output
```bash
* Current chain height is: 1809
* Found miner output with value 10000000000000000000000000
* Found miner output with value 10000000000000000000000000
* Found miner output with value 10000000000000000000000000
* Found miner output with value 10000000000000000000000000
* Found miner output with value 11000000000000000000000000
* Found miner output with value 11000000000000000000000000
* Found transaction output for address 02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754
* Found a spent address 822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb

```

After syncing your wallet, you can create and commit transactions
```python
    recipient = 'e5bd83a85e263817e2040054064575066874ee45a7697facca7a2721d4792af374ea35f549a1'
    transacton = rivine_wallet.create_transaction(amount=10, recipient=recipient)
    # you can then review the transaction by calling transaction.json
    transaction.json
    rivine_wallet.commit_transaction(transaction=transaction)
```