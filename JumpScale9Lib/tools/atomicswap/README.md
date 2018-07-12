# JumpScale Atomicswap SAL
This is a Software Abstraction Layer that allow jumpscale users to execute across chain atomicswaps.
The SAL provides the user with APIs that allows:
- Single API for executing a full automatic atomicswap
- Create an atomicswap initiator that supports initiate, audit, and redeem operations
- Create an atomicswap participant that supports participate, audit, and redeem operations

## Configurations
You can configure some environment variable to customize the behavior of the SAL specially if you are going to use the single API for executing a full atomicswap.
The following environment variables can be set:
- BTC_MIN_CONFIRMATIONS: This controls the number of confirmations the on the BTC network the SAL will wait for after creating a new transaction [default: 6]
- TFT_MIN_CONFIRMATION_HEIGHT: This controls the minimum height difference between a transaction and the chain height before considering the transaction confirmed [default: 5]
- BTC_RPC_USER: User name to use when connecting to the BTC daemon over RPC [default: user].
- BTC_RPC_PASS: Password to use when connecting to the BTC daemon over RPC [default: pass].
- BTC_RPC_ADDRESS: Address in the form of ip:port of the BTC daeomn [default: 'localhost:8332'].
- TFT_DAEMON_ADDRESS: Address in the form of ip:port of the TFchain daemon[default: 'localhost:23110'].

## Preparing the nodes
To run the SAL you will need to have two systems (one initiator and one participant), each system will need to run a full node from all the blockchains that you will need to use for atomicswaps (for now that is being TFChain and Bitcoin)
We provide prefab modules to install these blockchains, an example would look like:
```python
<prefab>.blockchain.bitcoin.install()
<prefab>.blockchain.tfchain.install()
```

In addition to the blockchain daemons, you also need to have the atomicswap binary, you can get this using the prefab module
```python
<prefab>.blockchain.atomicswap.install()
```

For the TFChain node, the following status is expected:
- The wallets are initialized and unlocked


## How to use it
### Single call atomicswap
The SAL provides a single API that warps the whole atomicswap operation, to get more information about what kind of arguments the API is expecting, you can check it using the jumpscale shell
```python
In [1]: j.tools.atomicswap.execute?
Signature: j.tools.atomicswap.execute(initiator_prefab, initiator_address, initiator_amount, participant_prefab, participant_address, participant_amount, testnet=False)
Docstring:
Executes a full cross chains atomicswap operation. This might take a long time depending on the confirmation time that each blockchain
netowrk will take.

@param initiator_prefab: Prefab object connecting to the atomic swap initiator node
@param initiator_address: Address from the participant network to recieve funds on
@param initiator_amount: Amount in the initator currency in the format '0.00024XXX' where XXX is the currency code, must be one of the following
('BTC', 'TFT', 'ETH', 'XRP')
@param participant_prefab: Prefab object connecting to  the atomic swap participant node.
@param participant_address: Address from the initiator network to recieve funds on.
@param participant_amount: Amount in the participant currency in the format '0.0000XXX' where XXX is the currency code, must be one of the following
('BTC', 'TFT', 'ETH', 'XRP')
@param testnet: If True, testnet is going to be used when doing the atomicswap [False by default]
File:      /home/abdelrahman/work/gig/jumpscale/lib9/JumpScale9Lib/tools/atomicswap/AtomicSwapFactory.py
Type:

```

An example call to the API and the expected output looks like:
```python
participant_address = 'mhv5Tve23BkVD6a8tpWKFxzWkub2sfiRqv'
initiator_address = '013803e566cdc065c415b14a1f082f240e8cc81a6f13fd01ef59e94620601a5a2f26e83b806091'
initiator_amount = 0.01234
participant_amount = 0.5
testnet = True

btc_prefab = j.tools.prefab.getFromSSH('localhost', port=2200)
tft_prefab = j.tools.prefab.getFromSSH('localhost', port=2222)
j.tools.atomicswap.execute(initiator_prefab=btc_prefab, initiator_address=initiator_address,
                          initiator_amount='{}BTC'.format(initiator_amount),
                          participant_prefab=tft_prefab,
                          participant_address=participant_address,
                          participant_amount='{}TFT'.format(participant_amount),
                          testnet=testnet)

* Starting atomicswap operation
* Intiating the atomicswap
* Waiting for transaction 5ec1bdea60804dd257e201ba28b5f5c3b49865ec570af9e6402c62a67010a263 to have at least 1 confirmations
* Waiting for participant node to be synced
* Executing paricipate operation
* Waiting for transaction 3011b5bd9598629ef418338460a18296ae0c3a74ea58fd465b901a7db8bf218b to have at least 2 height difference
* Waiting for initiator node to be sycned
* Initiator redeeming the contract
* Waiting for transaction e2543a3cf9657c357ab439bed09c29fd558ac2bb50ea5c2688efb907a882c5bf to have at least 2 height difference
* Participant redeeming the contract
* Waiting for transaction 6bbed4f228c5d3c242e6765df56e7b40bc441552480a6239b36a567710262a6e to have at least 1 confirmations

```

### Atomicswap APIs
Other than the single call atomicswap, you can use the SAL to have more control over the atomicswap process.
You can do this by creating an initiator and participant objects and execute the different APIs that they expose.

#### Creating an Initiator
Right now the SAL only supports BTC initiators, to create one you can use the following example
```python
participant_address = 'mhv5Tve23BkVD6a8tpWKFxzWkub2sfiRqv'
initiator_amount = 0.01234
testnet = True

initiator = j.tools.atomicswap.get_btc_initiator('localhost:2200', initiator_amount,
                                                 participant_address, testnet)
```

once you have created the initiator you can execute the following operations
- Initiate an atomicswap process
  ```python
    initiator.initiate()
  ```
- Audit the contract after participant executed the participate operation
  ```python
    initiator.auditcontract(output_id=<output_id>,
                                recipient_addr=<recipient_addr>,
                                secret_hash=<secret_hash>,
                                amount=<amount>)
  ```
- Redeem the amount from the contract
  ```python
    initiator.redeem(output_id=<output_id>,
                     secret=<secret>)
  ```

#### Creating a Participant
You can also create a participant (only TFT participants are supported at the moment)
```python
initiator_address = '013803e566cdc065c415b14a1f082f240e8cc81a6f13fd01ef59e94620601a5a2f26e83b806091'
initiator_amount = 0.01234
testnet = True

participant = j.tools.atomicswap.get_tft_participant('localhost:2222', participant_amount,
                                                initiator_address, testnet)

```
once you have created the participant you can execute the following operations

- Participate in an atomicswap process
  ```python
    participant.participate(secret_hash=<secret_hash>)
  ```
- Audit the contract
  ```python
    participant.auditcontract(contract=<contract>,
                            contract_txn=<contract_transaction>)
  ```
- Redeem the amount from the contract
  ```python
    participant.redeem(contract=<contract>, contract_txn=<contract_transaction>,
                        secret=<secrete>)
  ```
