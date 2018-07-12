"""
Fixers module
"""

from JumpScale9Lib.clients.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY
from JumpScale9Lib.clients.rivine.types.signatures import Ed25519PublicKey
from JumpScale9Lib.clients.rivine import utils, RivineWallet
import pytest
import ed25519


@pytest.fixture(scope="module")
def ats_hashed_secret():
    """
    Generate an atomicswap contract hashed secret
    """
    return "b5011ef9e6e03dcce148282ead7dd1cdf6f397d1c05680e8f12f39ba7b9c5dc4"


@pytest.fixture(scope="module")
def ats_secret():
    """
    Generate an atomicswap contract secret
    """
    return "603eb3efa05660fe04ea1cf391d8164265721eb8acd7f071c8c37de0f2214460"

@pytest.fixture(scope="module")
def recipient():
    """
    Generates a recipient address
    """
    hash = utils.hash(b'hello recipient')
    return str(UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash))

@pytest.fixture(scope="module")
def ulh():
    """
    Generates a test unlockhash of with unlock type publickey
    """
    hash = utils.hash(b'hello')
    return UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)

@pytest.fixture(scope="module")
def spendable_key():
    """
    Generates a test SpendableKey
    """
    sk, pk = ed25519.create_keypair(entropy=lambda x: b'a'*64)
    return RivineWallet.SpendableKey(pub_key=pk.to_bytes(), sec_key=sk)


@pytest.fixture(scope="module")
def ed25519_key(spendable_key):
    """
    Creates a test Ed25519PublicKey
    """
    return Ed25519PublicKey(pub_key=spendable_key.public_key)
