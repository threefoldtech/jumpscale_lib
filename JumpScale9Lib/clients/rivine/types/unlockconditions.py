"""
Unlockconditions module
"""

class SingleSignatureFulfillment:
    """
    SingleSignatureFulfillment class
    """
    def __init__(self, pub_key):
        """
        Initialzies new single singnature fulfillment class
        """
        self._pub_key = pub_key
        self._signature = bytearray()
