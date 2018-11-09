# Jumpscale Client for Rivine

## Rivine client usage

The rivine client itself is only intended as a library for other projects, such
as [TfChain](../tfchain/README.md). If you are interested in using a client, please
check the client of the correct chain, rather than this library.

## Provided functionality

This is a thin client/wallet for Rivine blockchains.
This means that it communicates with full nodes but does not store the blockchain locally and does not participate in the peer to peer protocol.

It supports the following functionalities:

- Starting from a seed, generate addresses and it's private keys.
- These addresses can be used to get the balances ( outputs)
- Remove those that are already spent
- When creating a transaction, select and use the the right amount of unspent outputs as inputs to have equal or more coins than the required output + transactionfee. Change can be written back to one of your own addresses.
- Initiate/participate in atomic swaps
- Create and spend multisig outputs


# Dependencies
The client depends on the following python libraries to be able to function properly:
- ed25519
- pyblake2

If you installed jumpscale on your system in dev mode and without setting the full installation flag (JSFULL=1) then you will need to install these libs manually if you want to continue using the client, to do that simply execute the following commands:
```python
pip3 install ed25519
pip3 install pyblake2
```


# How to use

## Creating a wallet

A wallet is a collection of addresses but  addresses are not random, they are generated from a single seed so it can be fully restored using this seed as well.

A seed which is a random byte array translated to a sentence of [12, 15, 18, 21, 24] words, for more information see https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

You can generate new seed by using the following commands in your js9 shell
```python
seed = j.clients.rivine.generate_seed()
```

From a seed you can create new wallet
```python
        from JumpscaleLib.clients.blockchain.rivine.RivineWallet import RivineWallet
        wallet = RivineWallet(seed=seed,
                                    bc_networks=['https://explorer.testnet.threefoldtoken.com/'],
                                    bc_network_password='test123',
                                    nr_keys_per_seed=1,
                                    minerfee=100000000)
        # where seed is the seed you have or generated
        # bc_networks: is list of the url to the blockchain network explorer nodes to try to connect to.
        # bc_network_password: is the password to use while communicating with the chain explorer node
        # nr_keys_per_seed: is how many keys to generate per seed
        # minerfee: How many hastings should be added as minerfee
```

Or alternatively you can configure the wallet instance using the following code:
```python
    client_data = {'bc_addresses': ['https://explorer.testnet.threefoldtoken.com/'],
'password_': 'test123',
 'minerfee': 10,
 'nr_keys_per_seed': 1,
 'seed_': seed}

    rivine_client = j.clients.rivine.get('mytestwallet', data=client_data)
    rivine_client.config.save()
    wallet = rivine_client.wallet
```

## basic commands

After creating the wallet you can check your wallet balance
```python
        wallet.current_balance
```

You should see something similar to the following output
```bash
Out[2]: 16.7
```

You can check the addresses in your wallet
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
client_data = {'bc_addresses': ['https://explorer.testnet.threefoldtoken.com/'],
               'password_': 'test123',
               'minerfee': 100000000,
               'nr_keys_per_seed': 1
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
### Sending tokens  that require multiple participants to sign 

The jumpscale client support sending tokens  that requires multiple addresses to sign to be able to be spent.  Use the send_to_multisig method available in the wallet object:
```python
recipients = [bob_wallet.addresses[0],
              alice_wallet.addresses[0],
              carlos_wallet.addresses[0],
              sam_wallet.addresses[0]
              ]
required_nr_of_signatures = 3

wallet.send_to_multisig(amount=2, recipients=recipients, required_nr_of_signatures=required_nr_of_signatures)
```
The above commands will send 2 TF Tokens to a multi-signature wallet shared between the recipients, and if 3 out of the 4 participants sings the transaction then the 2 TF Tokens can be spent already.

### Sending tokens that require multiple participants to sign with lock period

You also set a lock period e.g couple of hours or days, setting the token to be locked until the period is reached. To do that, you can simply use the same as the previous steps but add a locktime to the send_to_multisig call
```python
recipients = [bob_wallet.addresses[0],
              alice_wallet.addresses[0],
              carlos_wallet.addresses[0],
              sam_wallet.addresses[0]
              ]
required_nr_of_signatures = 3
locktime = int(time.time() + 15 * 60) # 15 minutes locktime

wallet.send_to_multisig(amount=2, recipients=recipients,
                    required_nr_of_signatures=required_nr_of_signatures,
                    locktime=locktime)
```

### Spending tokens  that require multiple participants to sign
To be able to spend the tokens, first they need to be unlocked (the lock-period has passed) and then you will need to have the required number of signatures. The steps can be explained with the following example:
```python
#1. create a transaction that is not yet singed by any participants
**TODO**
amount = 1.9 # note that you need to take into consideration the .1 TFT default minerfee
recipient = wallet.addresses[0]
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

## 3Bot commands

Using the `threebot` property available in the `j.clients.tfchain` namespace
as `j.clients.tfchain.threebot` allows you to:

* [get the record of an existing 3Bot](#get-a-3bot-record);
* [register a new 3Bot by creating a 3bot record](#create-a-3bot-record);
* [update the record of an existing 3Bot](#update-a-3bot-record);
* [transfer one or multiple names between two existing 3Bots](#Transfer-names-between-3Bot-records).

Getting a 3Bot record requires only an identifier of a 3Bot.
The other methods require a wallet as well, as these methods require (3Bot)
transactions to be created and signed, and therefore require coin inputs to be funded and signed,
as well as the signature of the 3Bot owning the record(s) to be created/updated.

If you plan to do something other than getting the record of an existing 3Bot,
it is important that you understand how to use the wallet of `j.clients.tfchain` and what it is.
You can read more about the wallet earlier in this document in the
[Creating a wallet](#creating-a-wallet) and [basic commands](#basic-commands) chapters.

### Get a 3Bot record

In order to get the record of an existing 3Bot from the standard network
all you need to know is its (unique integral) identifier and the following method:
```python
In [1]: j.clients.tfchain.threebot.get_record(1) # get the record of the 3Bot with ID 1
Out [1]:
{'id': 1,
 'addresses': ['93.184.216.34', 'example.org', '0:0:0:0:0:ffff:5db8:d822'],
 'names': ['example.threebot'],
 'publickey': 'ed25519:dbcc428065c0bf15216884998400dc079b5ce3ec0ba4904aeaaec2ba19dfa1d6',
 'expiration': 1544344200}
```

Should you want to get a 3Bot record from _testnet_ you would instead do:
```python
In [1]: j.clients.tfchain.threebot.get_record(1, network_addresses=j.clients.tfchain.network.TESTNET.official_explorers())
Out [1]:
{'id': 1,
 'addresses': ['3bot.zaibon.be'],
 'names': ['tf3bot.zaibon'],
 'publickey': 'ed25519:72ebed8fd8b75fce87485ebe7184cf28b838d9e9ff55bbb23b8508f60fdede9e',
 'expiration': 1543650900}
```

You can also get a 3Bot record of any other private/dev network,
but this requires you to give the `network_addresses` manually.

### Create a 3Bot record

In order to register a new 3Bot, you need to create a (3Bot) record.
This can be done as follows:

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot identification using a public/private key pair of this wallet.
In[1]: wallet = j.clients.tfchain.open_wallet('mywallet')

# if no public key is given, a new key pair ill be generated within the given wallet,
# and the public key of that pair will be used. Should you want to use an existing key pair of that wallet,
# you can pass the public key to this function.
In[2]: j.clients.tfchain.threebot.create_record(wallet, names=['example.threebot'], \
    addresses=['93.184.216.34', 'example.org', '2001:db8:85a3::8a2e:370:7334'], months=24)
[Fri09 09:34] - RivineWallet.py   :200 :in.rivine.rivinewallet - INFO     - Current chain height is: 327
[Fri09 09:34] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction
[Fri09 09:34] - utils.py          :247 :lockchain.rivine.utils - INFO     - Transaction committed successfully
Out[2]: <JumpscaleLib.clients.blockchain.rivine.types.transaction.TransactionV144 at 0x7fd27e262eb8>
```

The network is defined here by the given wallet. It can work with any version-up-to-date (tfchain) network,
as long as the wallet is configured for the desired network.

When you register a 3Bot you do not know your unique identifier yet,
as it is only assigned upon creation of the record in the blockchain.
Therefore you'll need to wait until your committed transaction has been confirmed,
such that you can get the unique identifier of the registered 3Bot by passing
the used public key (in string format) to the ["Get a 3Bot record"](#get-a-3bot-record) functionality.

### Update a 3Bot record

In order to update an existing 3Bot, you need to update its (3Bot) record.
This can be done as follows:

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot transaction (as the 3Bot owning the record to be updated)
# using the existing public/private key pair of this wallet.
In[1]: wallet = j.clients.tfchain.open_wallet('mywallet')

# you can do any or more of the following:
# add addresses, remove addresses, add names, remove names, add (activity) months
In[2]: j.clients.tfchain.threebot.update_record(wallet,
    names_to_add=['anewname.formy.threebot'], names_to_remove['example.threebot'], \
    addresses_to_add['example.com'])
[Fri09 09:47] - RivineWallet.py   :200 :in.rivine.rivinewallet - INFO     - Current chain height is: 392
[Fri09 09:47] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction
[Fri09 09:47] - utils.py          :247 :lockchain.rivine.utils - INFO     - Transaction committed successfully
Out[2]: <JumpscaleLib.clients.blockchain.rivine.types.transaction.TransactionV145 at 0x7fd27e2abc50>
```

The network is defined here by the given wallet. It can work with any version-up-to-date (tfchain) network,
as long as the wallet is configured for the desired network.

### Transfer names between 3Bot records

Transferring names involves two 3Bots, meaning two different 3Bots have to sign,
and thus an additional step is required. The method does not take into account
that a wallet might own both 3Bots, and thus even in that scenario you will have
to execute the second step manually.

In case you own a name, and want to give it to another 3Bot,
you'll need to use this feature, as to not risk that someone else registers the name
in the time window between you removing it from bot A, and bot B claiming it
as part of a record update. Instead by using this feature,
the name gets removed from the first bot, and added to the second bot,
as part of the same transaction, making it completely secure.

Transferring names between two 3Bot can be done as follows:

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot transaction (as the 3Bot owning the record to be updated)
# using the existing public/private key pair of this wallet.
In[1]: wallet_b = j.clients.tfchain.open_wallet('wallet-b')

In[2]: sender_bot_id = 1

In[3]: receiver_bot_id = 2

# you can do any or more of the following:
# add addresses, remove addresses, add names, remove names, add (activity) months
In[4]: tx = j.clients.tfchain.threebot.create_name_transfer_transaction(wallet_a, \
    sender_bot_id, receiver_bot_id, ['example.threebot'])
[Fri09 08:31] - RivineWallet.py   :200 :in.rivine.rivinewallet - INFO     - Current chain height is: 20
[Fri09 08:31] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction

# pass the tx as json to the other 3Bot
In[5]: tx.json # using any side-channel or software as you choose
```

```python
# this wallet is used in order to fund the creation of the 3Bot (spending coin outputs),
# as well as to sign the 3Bot transaction (as the 3Bot owning the record to be updated)
# using the existing public/private key pair of this wallet.
In[1]: wallet_a = j.clients.tfchain.open_wallet('wallet-a')

# create a transaction object from the transaction json
In[2]: txn = j.clients.rivine.create_transaction_from_json(txn_json)

# sign and commit the tx, as you've seen before in other chapter of this document
In[3]: wallet_a.sign_transaction(transaction=txn, commit=True)
[Fri09 08:32] - RivineWallet.py   :586 :in.rivine.rivinewallet - INFO     - Signing Transaction
[Fri09 08:32] - utils.py          :247 :lockchain.rivine.utils - INFO     - Transaction committed successfully
```

The network is defined here by the given wallets. It can work with any version-up-to-date (tfchain) network,
as long as the wallets are configured for the (_same_) desired network.
