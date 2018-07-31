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
        from JumpScale9Lib.clients.blockchain.rivine.RivineWallet import RivineWallet
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
 'seed_': seed}

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

## MultiSignature transactions
Multisignatures transactions are special type of transactions. They allow you to send funds to multiple wallets and specify how many participants needs to sign the transaction before the funds can be used.
To learn more about the different use cases of Multi-Signatures transactions please check the docs [here](https://github.com/rivine/rivine/blob/master/doc/transactions/multisig.md)

### Creating Walllets
Beside the main wallet we created before in this document, we will create 4 more wallets and 1 Multisig wallet. To create the 4 extra wallets, you should run the following commands:
```python
client_data = {'bc_address': 'https://explorer.testnet.threefoldtoken.com/',
               'password_': 'test123',
               'minerfee': 100000000,
               'nr_keys_per_seed': 15
               }
bob_seed = 'easily comic language galaxy chalk near member project mind noodle height rice box famous before cancel traffic festival laugh exist trend ensure claw fish'
alice_seed = 'green industry hockey scrap below film stage fashion volcano quantum pilot sea fan reunion critic rack cover toy never warrior typical episode seed divide'
carlos_seed = 'basic ranch raise cattle giraffe boost joy release jazz gaze friend program warfare switch design outer excess echo phrase visual woman coyote bid genuine'
sam_seed = 'marine company planet empty marble salon summer van skirt valid venture drastic breeze cushion detect catalog radar thing renew magnet resource movie hill harsh'

client_data['seed_'] = bob_seed
bob_wallet = j.clients.rivine.get('bobwallet', data=client_data).wallet


client_data['seed_'] = alice_seed
alice_wallet = j.clients.rivine.get('alicewallet', data=client_data).wallet

client_data['seed_'] = carlos_seed
carlos_wallet = j.clients.rivine.get('carlos_wallet', data=client_data).wallet

client_data['seed_'] = sam_seed
sam_wallet = j.clients.rivine.get('sam_wallet', data=client_data).wallet

```
### Sending tokens to multiple participants

The jumpscale client support sending money to multiple wallets, to do that you need to use the send_to_many method available in the wallet object:
```python
recipients = [bob_wallet.addresses[0],
              alice_wallet.addresses[0],
              carlos_wallet.addresses[0],
              sam_wallet.addresses[0]
              ]
required_nr_of_signatures = 3

wallet.send_to_many(amount=2, recipients=recipients, required_nr_of_signatures=required_nr_of_signatures)
```
The above commands will send 2 TF Tokens to a multi-signature wallet shared between the recipients, and if 3 out of the 4 participants sings the transaction then the 2 TF Tokens can be spent already.

### Sending tokens to multiple participants with lock period

You also set a lock period e.g couple of hours or days, setting the token to be locked until the period is reached. To do that, you can simply use the same as the previous steps but add a locktime to the send_to_many call
```python
recipients = [bob_wallet.addresses[0],
              alice_wallet.addresses[0],
              carlos_wallet.addresses[0],
              sam_wallet.addresses[0]
              ]
required_nr_of_signatures = 3
locktime = int(time.time() + 15 * 60) # 15 minutes locktime

wallet.send_to_many(amount=2, recipients=recipients,
                    required_nr_of_signatures=required_nr_of_signatures,
                    locktime=locktime)
```

### Spending the tokens in multisig wallet
To spend the token sent to multiple participants you will need to create a multisig wallet
```python

cosigners = [bob_wallet.addresses[0],
              alice_wallet.addresses[0],
              carlos_wallet.addresses[0],
              sam_wallet.addresses[0]
              ]

required_sig = 3

client_data = {'bc_address': 'https://explorer.testnet.threefoldtoken.com/',
               'password_': 'test123',
               'minerfee': 100000000,
               'multisig': True,
               'cosigners': cosigners,
               'required_sig': required_sig
               }

multisig_wallet = j.clients.rivine.get('shared_wallet', data=client_data).wallet
```

Once you have created the wallet, you can already check the current balance
```python
multisig_wallet.current_balance
* Current chain height is: 80440
Out[38]: {'locked': 2.0, 'unlocked': 0.0}
```
The above command should show you both the locked and unlocked balance in the wallet.

To be able to spend the tokens, first they need to be unlocked (the lock-period has passed) and then you will need to have the required number of signatures. The steps can be explained with the following example:
```python
#1. create a transaction that is not yet singed by any participants
amount = 1.9 # note that you need to take into consideration the .1 TFT default minerfee
recipient = wallet.addresses[0]
txn_json = multisig_wallet.create_transaction(amount=amount,
                                             recipient=recipient)
# txn_json is a json representation of the transaction we just created, this should be sent to participants to sing it.

#2. Create a transaction object from the transaction json
txn = j.clients.rivine.create_transaction_from_json(txn_json)

#3. Bob signs the transaction
bob_wallet.sign_transaction(transaction=txn, multisig=True)

# send the json format of the transaction using json.dumps(txn.json) to alice to sign it

#3. Alice sings the transaction
alice_wallet.sign_transaction(transaction=txn, multisig=True)

# send the json format of the transaction using json.dumps(txn.json) to sam to sign it and then it will have enough signatures, so it can be pushed to the network already

#4. Sam signs and commit the transaction to the network
sam_wallet.sign_transaction(transaction=txn, multisig=True, commit=True)

```
