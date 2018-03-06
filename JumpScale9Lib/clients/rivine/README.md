# JumpScale Client for Rivine

The client work as a lightweight wallet for the Rivine blockchain network.
It supports the following functionalities:

- Starting from a seed, be able to derive the public and private keypairs.
- Use the public keys to create unlockcondition objects, which can be hashed to get the addresses.
- These addresses can be used to query the explorer to get the coininputs
- Remove those that are already spent
- When creating the transaction, select the coin inputs to have equal or more coins than the required output + minerfee. Change can be written back to one of your own addresses. Note that an input must be consumed in its entirety.
- For every public key in the input, the corresponding private key is required to sign the transaction to be valid


## Dependecies
The client uses the world list proposed in BIP-0039 and depends on the library provided them: https://github.com/trezor/python-mnemonic (pip install git+https://github.com/trezor/python-mnemonic.git)
To generate keypairs we depend on the ed25519 python implementation here: https://github.com/warner/python-ed25519 (pip install ed25519)

To generate UnlockHashes, we use merkletree implementation from here: https://github.com/Tierion/pymerkletools (pip install merkletools) 