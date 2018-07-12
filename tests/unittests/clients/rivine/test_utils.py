"""
Unittests for utils module
"""
from JumpScale9Lib.clients.rivine import utils
import pytest

def test_locktime_from_duration():
    """
    Tests parsing locktime from duration string
    """
    duration = ''
    with pytest.raises(ValueError):
        utils.locktime_from_duration(duration=duration)

    duration = '00h10m00s'
    assert utils.locktime_from_duration(duration=duration) == 600

    duration = '1h10m5s'
    assert utils.locktime_from_duration(duration=duration) == (1 * 60 * 60 + 10 * 60 + 5)


def test_get_secret():
    """
    Tests getting a new random secret
    """
    size = 32
    assert len(utils.get_secret(size=size)) == size
