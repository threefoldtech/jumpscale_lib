"""
Unittests for rivine binary encoding module
"""

from unittest.mock import MagicMock, patch
import JumpScale9Lib.clients.rivine.encoding.binary
from JumpScale9Lib.clients.rivine.encoding import binary


def test_encode_all():
    """
    Test encode_all function
    """
    with patch.object(JumpScale9Lib.clients.rivine.encoding.binary, "encode") as encode_mock:
        result = binary.encode_all(['hello', 15])
        assert encode_mock.call_count == 2
        assert type(result) == bytearray


def test_encode():
    """
    Test encode function
    """
    
