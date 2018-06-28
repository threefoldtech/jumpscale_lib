# JumpScale Atomicswap SAL
This is a Software Abstraction Layer that allow jumpscale users to execute across chain atomicswaps.
The SAL provides the user with APIs that allows:
- Single API for executing a full automatic atomicswap
- Create an atomicswap initiator that supports initiate, audit, and redeem operations
- Create an atomicswap participant that supports participate, audit, and redeem operations

## Configurations
You configure some environment variable to customize the behavior of the SAL specially if you are going to use the single API for executing a full atomicswap.
The following environment variables can be set:
- BTC_MIN_CONFIRMATIONS: This controls the number of confirmations the on the BTC network the SAL will wait for after creating a new transaction [default: 6]
- TFT_MIN_CONFIRMATION_HEIGHT: This controls the minimum height difference between a transaction and the chain height before considering the transaction confirmed [default: 5]
- BTC_RPC_USER: User name to use when connecting to the BTC daemon over RPC.
- BTC_RPC_PASS: Password to use when connecting to the BTC daemon over RPC.
- BTC_RPC_ADDRESS: Address in the form of ip:port of the BTC daeomn.
