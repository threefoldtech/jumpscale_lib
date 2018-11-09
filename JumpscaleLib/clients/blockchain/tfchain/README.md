# TfChain client for JumpScale

This is a thin client for the [Threefold Chain blockchain](https://github.com/threefoldfoundation/tfchain).
It works by communicating with the public explorer nodes. This client is leveraging the rivine
client, by adding some chain specific constants so the user does not need to bother with this.

## Dependencies

As the TfChain client is basically a wrapper for the rivine client, it has the same
dependencies, see [the rivine module README](../rivine/README.md).

## Usage

Start by creating a wallet:
```python3
wallet1  = j.clients.tfchain.create_wallet('wallet1')
```
Should you want to create a testnet/devnet walk you have to define the network value:
```python3
wallet1  = j.clients.tfchain.create_wallet('wallet1', network=j.clients.tfchain.network.TESTNET)
```
In case you already created a wallet, you can open it:
```python3
 wallet1 = j.clients.tfchain.open_wallet('wallet1')
 ```
Now that we have our wallet, we can get the addresses we already generated

```python3
wallet1.addresses
Out[10]: ['01ffffbd36a9d6c995a82c8e34d53cf9cbb13b2c55bed3fcc0020d9c0ff682cd8d45d2f41acbeb']
```

 Check the balance:

```python3
wallet1.current_balance
Out[11]:
Unlocked:

	0.0
```

And once we received some funds on one of the addresses: 

```python
wallet1.current_balance
Out[17]:
Unlocked:

	1000.0
```

### Sending funds

```python
# First create a new wallet and get the address we will send funds to
wallet2 = j.clients.tfchain.create_wallet('wallet2', network=j.clients.tfchain.network.TESTNET)
address = wallet2.addresses[0] # Take the first address from the list of addresses
# Send 20 tft which can be spend immediatly. The transaction is commited automatically
amount = 20
wallet1.send_money(amount, address)
# It probably takes some time before the transaction is added in a block.
# In the meantime, it can already be seen in the balance of wallet2 as "unconfirmed":
wallet2.current_balance
Out[5]:
Unlocked:

	0.0

Unconfirmed Balance:

	20.0

# Now send 20 tft which are timelocked until the 30th of october, 1 PM GMT
locktime = 1540904400 # unix timestamp
wallet1.send_money(amount, address, locktime=locktime)

# After the transactions have been confirmed, the wallet2 balance will show:
wallet2.current_balance
Out[9]: 
Unlocked:

	20.0

Locked:

	20.0 locked until 2018-10-30 13:00:00
```

Funds can also be sent to a multisig wallet. To do so, the `send_to_multisig` function
should be used. It is also possible to add optional data or a locking period here.


```python
# Create another wallet
wallet3 = j.clients.tfchain.create_wallet('wallet3', network=j.clients.tfchain.network.TESTNET)
# now create the list of addresses which can spend the funds
addresses = [wallet2.addresses[0], wallet3.addresses[0]]
# both addresses will need to sign
required_sigs = 2
# First send 10 tft, which can be spent immediately
amount = 10
wallet1.send_to_multisig(amount, addresses, required_sigs)
# Now send 5 more tft which are timelocked until the 30th of october, 1PM GMT
locktime = 1540904400
wallet1.send_to_multisig(amount, addresses, required_sigs, locktime=locktime)

# After the transactions have been confirmed, wallet2 and wallet3 will report the
# multisig outputs as part of their balance
wallet2.current_balance
Out[19]:
Unlocked:

	20.0

Locked:

	20.0 locked until 2018-10-30 13:00:00

Unlocked multisig outputs:

	Output id: 3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0

Locked multisig outputs:

	Output id: d5290bae4c86dc85d42dfa030cfcb2c8d17c88a3a4d43b4fb4e88da3c7e4895f
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0 locked until 2018-10-30 13:00:00
```

### Using a multisig wallet

```python
# check the available inputs
wallet2.check_balance
Out[31]
Unlocked:

	20.0

Locked:

	20.0 locked until 2018-10-30 13:00:00

Unlocked multisig outputs:

	Output id: 3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0

Locked multisig outputs:

	Output id: d5290bae4c86dc85d42dfa030cfcb2c8d17c88a3a4d43b4fb4e88da3c7e4895f
	Signature addresses:
		017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921
		019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43
	Minimum amount of signatures: 2
	Value: 5.0 locked until 2018-10-30 13:00:00

# send funds to our original wallet, 1 tft 
address = wallet1.addresses[0]
amount = 1
# select the inputids we want to spend, multiple can be given
tx = wallet2.create_multisig_spending_transaction('3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c',
						  recipient=address, amount=amount)
wallet2.sign_transaction(tx, multisig=True)
# Print the tx json so it can be passed to the other signer
tx.json
Out[36]:
{'version': 1,
 'data': {'coininputs': [{'parentid': '3706001cfd4b24b9521a38eaba4a2b5a495129e6df41c1a58c9717156f1e284c',
    'fulfillment': {'type': 3,
     'data': {'pairs': [{'publickey': 'ed25519:894d0138e5eef44dcea71ff5990ec3941cb1f9c10fda6935474b2054db8d45a3',
        'signature': '90ebde0eef55f18c8c7d6c48181a8f4dc727464a68fac425763acb77cefca401bb9eed93d5c21c9020c94e1d4a721814bcd33783caaf4a6b5fae1c4d427b9b0b'}]}}}],
  'coinoutputs': [{'value': '1000000000',
    'condition': {'type': 1,
     'data': {'unlockhash': '01eacabf383ece86d601f755a283f853c74d09c7a1e48d73af541e6267181c25a6a8fe98157a0e'}}},
   {'value': '3900000000',
    'condition': {'type': 4,
     'data': {'unlockhashes': ['017d1a4078e38dd38d15360364d5c884f8ef98b63d19cd7a0c791e7c9beaf9efd7e835f293f921',
       '019fca6d823c69c49da1ca2e962b98ed5ac221fd5a85aa550e00b8a80db91ee9cc7afa967f4a43'],
      'minimumsignaturecount': 2}}}],
  'minerfees': ['100000000']}}

# Other person loads the transaction so his wallet can sign
tx = j.clients.tfchain.create_transaction_from_json(...) # copy transaction json
# Sign and commit transaction
wallet3.sign_transaction(tx, multisig=True, commit=True)

# after the transaction is confirmed, the output is added to the balance of the wallet.
# likewise, timelocked tokens can be send like this
wallet2.current_balance
Out[45]: omitted for brevity

# lock until 30th october 1 PM GMT
locktime = 1540904400
tx = wallet2.create_multisig_spending_transaction('6c68623bdb50e3127606f845f7fa23f3849ff9752c8ec35517a8ccd677493368',
						  amount=amount, recipient=recipient, locktime=locktime)
wallet2.sign_transaction(tx, multisig=True)
# get transaction json and load it so the other person can sign
Out[48]: omitted for brevity

# sign and commit transaction
wallet3.sign_transaction(tx, multisig=True, commit=True)
```

## How to use AtomicSwap
The light wallet client supports the different atomicswap operations. It allows the user to:
- Initiate a new atomicswap contract
- Participate in an exsisting atomicswap contract
- Validate the information of an atomicswap contract
- Withdraw funds from atomicswap contract
- Refund funds from atomicswap contract

For more details about the atomicswap process, it is recommended to check the documentation at the Rivine offical repository here: https://github.com/rivine/rivine/blob/master/doc/atomicswap/atomicswap.md

Detailed documentation on how to use the atomicswap api of the JumpScale client can
be found in [the atomicswap documentation](../../../../docs/clients/blockchain/atomicswapwalkthrough.md).
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

