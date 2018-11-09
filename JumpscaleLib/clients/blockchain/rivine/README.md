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
seed = j.data.encryption.mnemonic_generate()
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
