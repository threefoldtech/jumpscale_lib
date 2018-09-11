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

```
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

## TODO: AtomicSwap and MultiSig wallet
