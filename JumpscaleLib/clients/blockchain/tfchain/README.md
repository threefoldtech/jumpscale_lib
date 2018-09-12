# TfChain client for JumpScale

This is a thin client for the [Threefold Chain blockchain](https://github.com/threefoldfoundation/tfchain).
It works by communicating with the public explorer nodes. This client is leveraging the rivine
client, by adding some chain specific constants so the user does not need to bother with this.

## Dependencies

As the TfChain client is basically a wrapper for the rivine client, it has the same
dependencies, see [the rivine module README](../rivine/README.md).

## Usage

Operation requires a wallet, which is essentially a seed. Using this seed, (and only
this seed), the wallet can be fully recovered at a later date, including by someone else.
The seed must never be shared with anyone.

In case the user does not yet have a seed, one can be generated as follows:

```python
j.clients.tfchain.generate_seed()
```

This will produce a 24 word mnemonic. A mnemonic is a human readable representation
of the seed, which is just a bunch of bytes. Some shorter mnemonics coudl be used,
however we always generate 32 byte seeds, which results in 24 word mnemonics when encoded.

Note that this step is optional. It is completely possible to create a tfchain wallet
without specifying a seed. In this case, the seed will be generated and saved as soon
as the wallet of the TfChain client is accessed for the first time.

We assume that JumpScale is being used to create the client, e.g.:

```python
cl = j.clients.tfchain.get('myclient', data=data, interactive=False)
```

data is a `dict` with config keys/values. The acceptible keys are:

 - `testnet (bool)`: Indicate that we should use testnet, defaults to False.
 - `multisig (bool)`: Defines if this is a multisig wallet or not, defaults to false
 - `seed_ (string)`: The seed to load as a mnemonic. If this is the empty string (default), a new one is generated
 - `nr_keys_per_seed (int)`: The amount of keys (addresses) to generate from the seed initially
 - `cosigners (list(str))`: A list of addresses which own the multisig wallet
 - `required_sig (int)`: The minimum amount of signatures required to spend an output from the multisig wallet
 
Note that the usage of either `seed_` and `nr_keys_per_seed`, or `cosigners` and `required_sig`
depends on the value of `multisig`. If `multisig` is false, the default, then only
the first 2 parameters will be used. Likewise if `multisig` is true, then only the
last 2 parameters are used.

In the following example, a testnet wallet is created, without a seed, and the default
amount of addresses is loaded:

```python
data = {}
data['testnet'] = True
cl = j.clients.tfchain.get('testnet_wallet', data=data, interactive=False)
wallet = cl.wallet
```

Now that we have our wallet, we can get the addresses we already generated

```python
wallet.addresses
```

And once we received some funds on one of these addresses, we can verify that:

```python
wallet.current_balance
```

### Sending funds

Sending funds to another wallet requires an address. Once the address has been
acquired, we can send the amount of TFT we want. Optionally, we could lock this amount
untill a certain block height or time, or we could add some extra data. Locking
and adding data is ofcourse optional. By default the transaction will send any
leftover funds from the inputs back to one of the input addresses. This behaviour
can be overrided by setting the `reuse_addr` parameter to `False`, which will force
generation of a new address to send the leftover funds to.

```python
address = '01fe9e3c3001ada8ed39248ec376133032067adf36f5fd2eac27363432a3b55945bcba2694f00b'
amount = 10 # Send 10 TFT
optional_data = b"a small optional message"
locktime = 120000 # lock until block 120.000
txn = wallet.send_money(amount, address, data=optional_data, locktime=locktime)
# In case you are interested, the transaction can be seen in its raw json form:
txn.json
```

The transaction will automatically be signed and send to the public explores, which
will then try to put it in the network.

Funds can also be send to a multisig wallet. To do so, the `send_to_many` function
should be used. It is also possible to add optional data or a locking period here.

```python
recipients = ['01b255ffb4a3b08822ce5d4e1118159ab781b7c1bb6b5913aba63625b943cff6de8bd740c38ea1',
	'01fe9e3c3001ada8ed39248ec376133032067adf36f5fd2eac27363432a3b55945bcba2694f00b']
required_nr_of_signatures = 2
amount = 5
wallet.send_to_many(amount, recipients, required_nr_of_signatures)
```

### Using a multisig wallet

A multisig wallet does not behave like the regular (single signature wallet). For
instance, there is only 1 address. A Multisig wallet also does not have a seed.
To create a multisigi wallet, the `cosigners` and `required_sig` property need to be
set when creating the wallet. Also, the `multisig` property needs to be set to `True`.

```python
# Create a multisig wallet for testnet, owned by 2 addresses, which will both need
# to sign in order to spend any funds
data = {}
data['cosigners'] = ['01b255ffb4a3b08822ce5d4e1118159ab781b7c1bb6b5913aba63625b943cff6de8bd740c38ea1',
	'01fe9e3c3001ada8ed39248ec376133032067adf36f5fd2eac27363432a3b55945bcba2694f00b']
data['required_sig'] = 2
data['multisig'] = True
data['testnet'] = True
clm = j.clients.tfchain.get('multisigwallet', data=data, interactive=False)
```

This will create a client (just as in the regular single sig wallet eample), with a
`wallet` property. This time, said wallet will be a multisig wallet, however. To
check if there are any tokens in the wallet, the current balance can be requested.

```python
clm.wallet.current_balance
```

Sending tokens requires some additional effort comapred to single signature wallets.
This is because we don't have the seeds of the addresses which can sign, and thus we
can't derive the required keys. As such, we can only create an unsigned transaction
with the required inputs and outputs. This transaction then needs to be distributed
to the owners of the addresses, who can then sign the transaction.

```python
raw_tx = clm.wallet.create_transaction(49.8, '01ff06362d16386bda7ab2226b215b247e48c235849c67c235972f6c86149aa035d88595ef2298')
```

This `raw_tx` is a json string, which can be distributed to the owners of the addresses
in this wallet. One of the addresses is owned by the single signature we used previously,
this is how we sign;

```python
# First we convert the json to a tx object
unsigned_tx = j.clients.tfchain.create_txn_from_json(raw_tx)
# Now load the wallet and try to sign the transaction
cl = j.clients.tfchain.get('testnet_wallet')
# Try to sign, and indicate that we try to sign a multisig input
signed_tx = j.clients.tfchain.sign_transaction(unsigned_tx, multisig=True)
# print the json form of the txn so we can send it to others
signed_tx.json
```

If we are the last to sign, the `commit` parameter can be set to `True`, which will
push the transaction to the public explorers, to get it included in the network. By default
it is not published.

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
