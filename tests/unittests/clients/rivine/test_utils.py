"""
Unittests for utils module
"""
import pytest
from unittest.mock import MagicMock, patch
from JumpscaleLib.clients.blockchain.rivine import utils
from JumpscaleLib.clients.blockchain.rivine.errors import RESTAPIError

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


@patch('JumpscaleLib.clients.blockchain.rivine.utils.requests.get')
def test_get_current_chain_height(mock_get):
    """
    Tests getting the current chain height
    """
    with pytest.raises(RESTAPIError):
        utils.get_current_chain_height([])

    mock_response = MagicMock()
    mock_response.status_code.return_value = 200
    mock_response.json.return_value = {'height': 10}
    mock_get.return_value = mock_response
    utils.get_current_chain_height(['https://explorer.testnet.threefoldtoken.com/'])
