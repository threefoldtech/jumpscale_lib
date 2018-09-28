# TfChain client for JumpScale

This is a thin client for the [Threefold Chain blockchain](https://github.com/threefoldfoundation/tfchain).
It works by communicating with the public explorer nodes. This client is leveraging the rivine
client, by adding some chain specific constants so the user does not need to bother with this.

## Dependencies

As the TfChain client is basically a wrapper for the rivine client, it has the same
dependencies, see [the rivine module README](../rivine/README.md).

## Usage

Start by creating a wallet ( for testnet in this case)
```python
wallet = j.clients.tfchain.create_wallet('default', testnet = True)
```
Or in case you already created a wallet, you can open it :
```python
 wallet = j.clients.tfchain.open_wallet('default')
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
### recovering a wallet 

A wallet is essentially a seed. Using this seed, (and only
this seed), the wallet can be fully recovered at a later date, including by someone else.
The seed must never be shared with anyone.
```python
seed = wallet.seed
newwallet =  j.clients.tfchain.create_wallet('default', seed=seed)
```

Instead of reusing the seed of an existing wallet, you can also generate a seed yourself and create wallets from that one.

```python
seed = j.clients.tfchain.generate_seed()
```

This will produce a 24 word mnemonic. A mnemonic is a human readable representation
of the seed, which is just a bunch of bytes. Some shorter mnemonics could be used,
however we always generate 32 byte seeds, which results in a 24 word mnemonics when encoded.

## Creating coins

Coin creation is handled by a "coin creation transaction" (transaction version 129).
In order to create coins, the `mint condition` needs to be fulfilled. The current
mint condition can be viewed using the `get_current_mint_condition` method on a wallet.

### Quick start

This section describes how to create a coin creation transaction as quickly as possible.
From start to finish, we perform the following steps:

- Create a condition, which will define how the output can be spent
- Create a new transaction, using this condition and a value
- Sign the transaction.

After this is done, the transaction likely needs to be signed by other people.

Our condition can be created by using the `create_singlesig_condition` or
`create_multisig_condition` methods on the tfchain client factory. The required
arguments are the unlockhash, and the list of unlockhashes + the minimum amount of
signatures required respectively. Both conditions can optionally be timelocked
by providing the `timelock` parameter.

Now that we have a condition, a transaction can be created using the
`create_coincreation_transaction` method. The previously created condition can be
given as an optional parameter (named `condition`). If the `value` parameter is also
set, an output will be created and added on the transaction. If wanted, a `description`
string can be given, which is set in the arbitrary data field.

Lastly, the transaction needs to be signed. If the wallet which does the signing does
not have any key capable of signing, nothing happens. Signing is done with the
wallet's `sign_transaction` method.

If the transaction then needs to be signed by others, it can be shared in its json
form. A json transaction can also be loaded.

Full example:

```python3
# Create the condition, we just want to send to an address here:
condition = j.clients.tfchain.create_singlesig_condition('01b4668a4b9a438f9143af8500f6566b6ca4cb3e3a3d98711deee3dee371765f58626809117a33')

# Create the transaction, sending 1 TFT ( = 1000000000 units)
# Also set an example description
tx = j.clients.tfchain.create_coincreation_transaction(condition=condition, value=1000000000, description='optional description')

# Try to add signatures
# Assume cl is a previously loaded client, see above
cl.wallet.sign_transaction(tx)

# Convert the transaction to json, so it can be shared to other signers
jsontx = tx.json

#Sign it through the a cosigner wallet 
tx = j.clients.tfchain.create_transaction_from_json(jsontx)
secondsignerwallet.sign_transaction(tx)

# the last signer commits it to the network as well
thirdsignerwallet.sign_transaction(tx, commit=True) 
```


### Full description

To get started, we first need to obtain such a transaction. A new one can be created,
after which we can add the coin outputs, or an existing one can be loaded from json.
To create a new (empty) coin creation transaction, the `create_coincreation_transaction()`
method on the tfchain client factory can be used:

```python
tx = j.clients.tfchain.create_coincreation_transaction()
```

Alternatively, to load one from json, the `create_transaction_from_json()` method
can be used:

```python
tx = j.clients.tfchain.create_transaction_from_json(_transaction json_)
```

Now that we have a transaction, we can add outputs. This functions just like regular
transactions: we can create either a single signature output, or a multisig output.
Both outputs can be timelocked as well. To send coins to a single sig address, the
`add_coin_output` method of the transaction can be used, with the amount to send
(expressed in base units), followed by the string representation of the destination address
as parameters, for instance:

```python
tx.add_coin_output(1000000000,
	'013a787bf6248c518aee3a040a14b0dd3a029bc8e9b19a1823faf5bcdde397f4201ad01aace4c9')
```

In the above snippet, a new output is added in which 1 TFT is send to the specified address.
Should this be required, the `locktime` parameter can be added, with a given block height
or unix timestamp untill which the output will be timelocked.

Likewise, a multisig output can be added by using the `add_multisig_output` method.
As with singe sig outputs, the first parameter is the amount to send, followed by the
addresses which can spend said multisig output, and then the mininimum amount of
signatures required to spend (similar to adding a multisig output to a regular
transaction). If required, the `locktime` parameter can once again be specified to
time lock the output.

It is important to note that outputs can only be added before any signature is added,
as with regular transaction.

Arbitrary data can be set on the transaction. This can be done with the `add_data` method.
Note that the maximum length of the arbitrary data can be at most 83 bytes, if there
is more data then the transaction will be rejected.

Likewise additional minerfees can be specified with the `add_minerfee` method. Since
we are creating coins, we are also creating the minerfee, so there is no need to add
any input for this.

Signing this transaction can be done using a tfchain wallet. Using the wallet's
`sign_transaction` method will greedily add a signature for any applicable key
loaded in said wallet, based on the current mint condition. Once your signature
is added, the transaction json can be distributed to the other coin creators, or if enough
signatures are added, the transaction can be published to the chain. If you want to
try and commit the transaction after signing it, the `commit` parameter can be set to
`True` when calling the signing method.

Example of signing a transaction:

```python
cl.wallet.sign_transaction(tx, commit=True)
```

## minter definition transaction

By using transaction version 128, a new minter condition can be specified. The minter
condition defines who can create coins. Redefining the minter definition is largerly
the same as creating new coins, so only the differences are covered here:

Creating a new minter definition transaction is done with the `create_minterdefinition_transaction`
method of the tfchain client factory.

There are no coin outputs, only a single condition, which becomes the new minter definition.
This means that, in order to create coins, this condition will need to be fulfilled after
this transaction has been published and accepted on the chain. The new mint condition
can be either a single sig or multisig condition (in practice this should always be a
multisig). The condition can be added by using the `set_singlesig_mint_condition`
and `set_multisig_mint_condition` methods of the transaction.

These are the only differences. The transaction can be signed exactly the same like
a regular coin creation transaction.
