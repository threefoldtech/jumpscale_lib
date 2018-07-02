"""
Fixers module
"""

from JumpScale9Lib.clients.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY
from JumpScale9Lib.clients.rivine import utils
import pytest

@pytest.fixture(scope="module")
def ulh():
    hash = utils.hash(b'hello')
    return UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
