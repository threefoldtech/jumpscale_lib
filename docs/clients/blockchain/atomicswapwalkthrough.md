# Cross chain atomic swap walkthrough using the jumpscale thin clients.

## required tools  
In order to execute atomic swaps as described in this document, you need to have the [Electrum wallet](https://electrum.org/) and the Decred atomic swap tools that are available at <https://github.com/rivine/atomicswap/releases>.

The original decred atomic swap project is [Decred atomic swaps](https://github.com/decred/atomicswap), the rivine fork just supplies the binaries.

### To install the required tools you can execute the following in your js shell
```
j.tools.prefab.local.blockchain.electrum.install(reset=True)
j.tools.prefab.local.blockchain.atomicswap.install(reset=True, tag=None, branch='json')
```

## Example

Let's assume Bob wants to buy 10 TFT from Alice for 0.1234BTC

Bob creates a bitcoin address and Alice creates a threefold address.

Bob initiates the swap, he generates a 32-byte secret and hashes it
using the SHA256 algorithm, resulting in a 32-byte hashed secret.

Bob now creates a swap transaction, as a smart contract, and publishes it on the Bitcoin chain, it has 0.1234BTC as an output and the output can be redeemed (used as input) using either 1 of the following conditions:
- timeout has passed (48hours) and claimed by Bob's refund address;
- the money is claimed by Alice's registered address and the secret is given that hashes to the hashed secret created by Bob

This means Alice can claim the bitcoin if she has the secret and if the atomic swap process fails, Bob can always reclaim it's btc after the timeout.

 Bob sends this contract and the transaction id of this transaction on the bitcoin chain to Alice, making sure he does not share the secret of course.

 Now Alice validates if everything is as agreed (=audit)after which She creates a similar transaction on the Rivine chain but with a timeout for refund of only 24 hours and she uses the same hashsecret as the first contract for Bob to claim the tokens.
 This transaction has 9876 tokens as an output and the output can be redeemed( used as input) using either 1 of the following conditions:
- timeout has passed ( 24hours) and claimed by the sellers refund address
- the secret is given that hashes to the hashsecret Bob created (= same one as used in the bitcoin swap transaction) and claimed by the buyers's address

In order for Bob to claim the threefold tokens, he has to use and as such disclose the secret.

The magic of the atomic swap lies in the fact that the same secret is used to claim the tokens in both swap transactions but it is not disclosed in the contracts because only the hash of the secret is used there. The moment Bob claims the threefold tokens, he discloses the secret and Alice has enough time lef to claim the bitcoin because the timeout of the first contract is longer than the one of the second contract.
Of course, either Bob or Alice can be the initiator or the participant.

## Technical details of the example
This example is a walkthrough of an actual atomic swap  on the threefold and bitcoin testnets.


Start Electrum on testnet and create a default wallet but do not set a password on it:

Configure and start Electrum as a daemon :
```
j.tools.prefab.local.blockchain.electrum.start(rpcuser='user', rpcpass='pass', rpcport=7777, rpchost='localhost', testnet=True)
```
While the daemon is running, create a new wallet from existing seed or new seed, in your js shell:
```
seed = <existing_seed> or j.clients.btc_electrum.generate_seed(256)
data_dir = '/root/opt/var/data/electrum'
rpcuser = 'user'
rpcpass = 'pass'
rpcport = 7777
rpchost= 'localhost'
wallet_name = 'mybtcwallet'

client_data = {
  'server': "{}:{}:s".format(rpchost, rpcport),
  'rpc_user': rpcuser,
  'rpc_pass_': rpcpass,
  'seed_': seed,
  'password_': "",
  "passphrase_": "",
  "electrum_path": data_dir,
  "testnet": 1
}

electrum_cl = j.clients.btc_electrum.get(instance=wallet_name,data=client_data)
electrum_cl.config.save()

# check your current balance
electrum_cl.wallet.getbalance()
```

Alice creates a new bitcoin address and provides this to Bob:
```￼
btcwallet = j.clients.btc_electrum.get('mybtcwallet').wallet
In [6]: btcwallet.getunusedaddress()
Out[6]: 'n2Z59eL34Vpfd4p726JjnHsNmTXSeaRn9s'
```

### initiate step
Bob initiates the process by using btcatomicswap to pay 0.1234BTC into the Bitcoin contract using Alice's Bit coin address, sending the contract transaction, and sharing the secret hash (not the secret), and contract's transaction with Alice. The refund transaction can not be sent until the locktime expires, but should be saved in case a refund is necessary.


```
electrum_cl = j.clients.btc_electrum.get(instance='mybtcwallet')

In [16]: electrum_cl.atomicswap.initiate('mxzXMShoYyD1UndzDuCzgbZXc3vNbNdLj9', 0.1234)
[Mon24 06:14] - ElectrumAtomicswap.py:63  :rum.electrumatomicswap - INFO     - Initiating a new atomicswap contract using command: btcatomicswap -testnet -automated --rpcuser=user --rpcpass=pass -s "localhost:7777" initiate n2Z59eL34Vpfd4p726JjnHsNmTXSeaRn9s 0.1234
[Mon24 06:14] - PrefabCore.py     :1123:j.prefabcore         - INFO     - RUN:btcatomicswap -testnet -automated --rpcuser=user --rpcpass=pass -s "localhost:7777" initiate n2Z59eL34Vpfd4p726JjnHsNmTXSeaRn9s 0.1234
Out[20]:
{'secret': 'd3a35a9fb9f23440050783a2b66f7a2f4628b33350a821969af1828c782bb12f',
 'hash': '7e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a5',
 'contractfee': '0.0000186 BTC',
 'refundfee': '0.00001483 BTC',
 'contractp2sh': '2NGGNvzbYZJVCYsKiqDJqA6Y2iahFvMoFru',
 'contract': '6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac',
 'contractTransactionHash': '5d3fa809b60ff2f6bc078df78572ea88d67cb5b0d3f53557c66921f0325d9eda',
 'contractTransaction': '0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500',
 'refundTransactionHash': '1115d9b95bf7fcf445278ae3d0dd8b82e9f24c8fbfa01020acf36a45f6ec0e0d',
 'refundTransaction': '0200000001da9e5d32f02169c65735f5d3b0b57cd688ea7285f78d07bcf6f20fb609a83f5d01000000cf483045022100d2e4ec77eb07e19e4bf5621cbb53095c09b0db3b799fbcfc0e9f64d2246f7cd502207bfee30c3da730906c527fa4edb86af07281d9e2ded6e48fd8f7702060ea054f012103f708d747a00468ecb3c653e44e026e46def9aab9929bb63facbcae1a7c7c9265004c616382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac00000000015445bc00000000001976a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c88acc323ab5b'}
```
You can check the transaction [on a bitcoin testnet blockexplorer](https://testnet.blockexplorer.com/tx/5d3fa809b60ff2f6bc078df78572ea88d67cb5b0d3f53557c66921f0325d9eda) where you can see that 0.1234 BTC is sent to 2NGGNvzbYZJVCYsKiqDJqA6Y2iahFvMoFru (= the contract script hash) being a [p2sh](https://en.bitcoin.it/wiki/Pay_to_script_hash) address in the bitcoin testnet.


 ### audit contract

Bob sends Alice the contract and the contract transaction. Alice should now verify if
- the script is correct
- the locktime is far enough in the future
- the amount is correct
- she is the recipient

API: `electrum_cl.atomicswap.auditcontract(contract, contract_transaction)`

 ```
 In [1]: electrum_cl = j.clients.btc_electrum.get('mybtcwallet')
 In [4]: electrum_cl.atomicswap.auditcontract('6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac', '0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500')
 [Mon24 06:16] - ElectrumAtomicswap.py:105 :rum.electrumatomicswap - INFO     - Auditing an atomicswap contract using command: btcatomicswap -testnet -automated --rpcuser=user --rpcpass=pass -s "localhost:7777" auditcontract 6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac 0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500
 [Mon24 06:16] - PrefabCore.py     :1123:j.prefabcore         - INFO     - RUN:btcatomicswap -testnet -automated --rpcuser=user --rpcpass=pass -s "localhost:7777" auditcontract 6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac 0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500
 Out[22]:
 {'contractAddress': '2NGGNvzbYZJVCYsKiqDJqA6Y2iahFvMoFru',
  'contractValue': '0.12339999 BTC',
  'recipientAddress': 'n2Z59eL34Vpfd4p726JjnHsNmTXSeaRn9s',
  'refundAddress': 'mwWkTFMcarG2ij3iUh26U68EA7iM1HmQuE',
  'secretHash': '7e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a5',
  'Locktime': '2018-09-26 06:14:27 +0000 UTC'}

```

WARNING:
A check on the blockchain should be done as the auditcontract does not do that so an already spent output could have been used as an input. Checking if the contract has been mined in a block should suffice

### Participate

Alice trusts the contract so she participates in the atomic swap by paying the tokens into a threefold token  contract using the same secret hash.

Bob creates a new threefold address ( or uses an existing one):
```
In [10]: tftwallet = j.clients.rivine.get('mytftwallet').wallet

In [11]: tftwallet.generate_address()
Out[11]: '01c9021185654ed4a50e05d28a2fe06d1f9cdd7f6205eff0951102a9d772b2f39c58dbe8b8c9d8'
```

Bob sends this address to Alice who uses it to participate in the swap.
command:`tftwallet.atomicswap.participate(initiator_address, amount, hashed_secret, duration='24h0m0s', refund_address=None)`
```
In [10]: tftwallet.atomicswap.participate('01c9021185654ed4a50e05d28a2fe06d1f9cdd7f6205eff0951102a9d772b2f39c58dbe8b8c9d8', 10, '7e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a5')
[Mon24 06:19] - RivineWallet.py   :149 :in.rivine.rivinewallet - INFO     - Current chain height is: 120704
[Mon24 06:19] - RivineWallet.py   :433 :in.rivine.rivinewallet - INFO     - Signing Trasnaction
[Mon24 06:19] - utils.py          :221 :lockchain.rivine.utils - INFO     - Transaction committed successfully
Out[23]:
{'amount': 10,
 'hashed_secret': '7e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a5',
 'transaction_id': 'aec2afdb538136855c3b7af0c3fe71f6db5b7978803597279458e5273894ce38',
 'output_id': '488e3f554389e5bca30b70fd78b65810a590f90b0680acb71b56fdb4bfaa24fa'}

```

The above command will create a transaction with `10` TFT as the Output  value of the output (`aec2afdb538136855c3b7af0c3fe71f6db5b7978803597279458e5273894ce38`). The output can be claimed by Bobs address (`01c9021185654ed4a50e05d28a2fe06d1f9cdd7f6205eff0951102a9d772b2f39c58dbe8b8c9d8`)  and Bob will  to also have to provide the secret that hashes to the hashed secret `7e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a5`.

Alice now informs Bob that the Threefold contract transaction has been created and provides him with the contract details.

### audit Threefold contract

Just as Alice had to audit Bob's contract, Bob now has to do the same with Alice's contract before withdrawing.
Bob verifies if:
- the amount of threefold tokens () defined in the output is correct
- the attached script is correct
- the locktime, hashed secret (`ed737797f815bb446658f4a9979a48f37c5772e5dd1d897454cb66bcc8265739`) and wallet address, defined in the attached script, are correct

command:`tftwallet.atomicswap.validate(transaction_id, amount=None, hashed_secret=None, receiver_address=None, time_left=None)`
flags are available to automatically check the information in the contract.
```
In [5]: tftwallet.atomicswap.validate('aec2afdb538136855c3b7af0c3fe71f6db5b7978803597279458e5273894ce38', amount=10, hashed_secret='7e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a5')
Out[5]: True
```

The audit also checks if that the given contract's output  has not already been spend.

### redeem tokens

Now that both Bob and Alice have paid into their respective contracts, Bob may withdraw from the Threefold contract. This step involves publishing a transaction which reveals the secret to Alice, allowing her to withdraw from the Bitcoin contract.

command:`tftwallet.atomicswap.redeem(transaction_id, secret)`

```
In [3]: tftwallet.atomicswap.redeem('aec2afdb538136855c3b7af0c3fe71f6db5b7978803597279458e5273894ce38', 'd3a35a9fb9f23440050783a2b66f7a2f4628b33350a821969af1828c782bb12f')
[Mon24 06:22] - utils.py          :221 :lockchain.rivine.utils - INFO     - Transaction committed successfully
[Mon24 06:22] - atomicswap.py     :245 :.atomicswap.atomicswap - INFO     - Redeem executed successfully. Transaction ID: 6a2ca8524462bc638f245beab6074e4c31e9291d986ebb20748223ef21281632
Out[25]: '6a2ca8524462bc638f245beab6074e4c31e9291d986ebb20748223ef21281632'
```

### redeem bitcoins

Now that Bob has withdrawn from the rivine contract and revealed the secret. If bob is really nice he could simply give the secret to Alice. However,even if he doesn't do this Alice can extract the secret from this redemption transaction. Alice may watch a block explorer to see when the rivine contract output was spent and look up the redeeming transaction.

Alice can automatically extract the secret from the input where it is used by Bob, by simply giving the TransactionID of the contract. You can do this using a public web-based explorer, by looking up the TransactionID as hash


With the secret known, Alice may redeem from Bob's Bitcoin contract:
command: `electrum_cl.atomicswap.redeem(contract, contract_transaction, secret)`
```
electrum_cl = j.clients.btc_electrum.get(instance="mybtcwallet")

In [28]: electrum_cl.atomicswap.redeem('6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba840f1ee0c52c6414c6888ac','0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500','d3a35a9fb9f23440050783a2b66f7a2f4628b33350a821969af1828c782bb12f')
[Mon24 06:25] - ElectrumAtomicswap.py:147 :rum.electrumatomicswap - INFO     - Redeeming the atomicswap contract using command: btcatomicswap -testnet -automated --rpcuser=user --rpcpass=pass -s "localhost:7777" redeem 6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac 0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500 d3a35a9fb9f23440050783a2b66f7a2f4628b33350a821969af1828c782bb12f
[Mon24 06:25] - PrefabCore.py     :1123:j.prefabcore         - INFO     - RUN:btcatomicswap -testnet -automated --rpcuser=user --rpcpass=pass -s "localhost:7777" redeem 6382012088a8207e8092e3174c23d52af9fb7dd0c0fd73e037ece078406a993afebe1bc7f476a58876a914e6c132166626fa04e5c816db9bc0c7f89dd19c6d6704c323ab5bb17576a914af7820b5b798d8b930e4ba8450f1ee0c52c6414c6888ac 0100000002a252c968ec3886b826b13467fa1421a65e081c7202f0b068945e6295e8d05254010000006a4730440220340f84669207677503d739a8e3e0381a2a8a7a05e372582506aab86fdc157ffe02205cceb72ddbf39cd5094e143bc8829045a60558d46d00a5f31476b1cdcefe93d5012103bb05d3f944e43dfb7d47515448c47147332bff8e5aebb1d1a2059c6e95d88aaafdffffff0deb5702adf046f30c45fb0f8eb105204e72680586b65bc0835ec4de86915567000000006a4730440220766bb11d62df865c3f4d79e31f98cfba54f5ad1d5b65affbf3c463f8dfc71e070220232f673254584ab6bb571ebac23405926f367b91c4313b885344c6c0968ae60701210344f298802544dd6dca01d0435447e72ccfb49d7ba185de9d0388260bb14dd7a5fdffffff0241670400000000001976a9143ffc356766971b93af24c004cf535d392a81149988ac1f4bbc000000000017a914fc82c642de96f175f5a8f540cf30c7c58f1971ac8731941500 d3a35a9fb9f23440050783a2b66f7a2f4628b33350a821969af1828c782bb12f
Out[28]:
{'redeemFee': '0.00001648 BTC',
 'redeemTransaction': 'b378b962492834f9f78bb94aee5d0479ce719e4fce062307fefbf3520f5a0eda'}
```
This transaction can be verified [on a bitcoin testnet blockexplorer](https://testnet.blockexplorer.com/tx/b378b962492834f9f78bb94aee5d0479ce719e4fce062307fefbf3520f5a0eda) .
The cross-chain atomic swap is now completed and successful.

## References

- [Electrum](https://electrum.org)
