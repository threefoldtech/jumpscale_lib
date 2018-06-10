"""
Unlockconditions module
"""

from JumpScale9Lib.clients.rivine.errors import DoubleSignatureError

class SingleSignatureFulfillment:
    """
    SingleSignatureFulfillment class
    """
    def __init__(self, pub_key):
        """
        Initialzies new single singnature fulfillment class
        """
        self._pub_key = pub_key
        self._signature = None

    def sign(self, sig_ctx):
        """
        Sign the given fulfillment, which is to be done after all properties have been filled of the parent transaction

        @param sig_ctx: Signature context should be a dictionary containing the secret key, input index, and transaction object
        """
        if self._signature is not None:
            DoubleSignatureError("cannot sign a fulfillment which is already signed")



class UnlockHashCondition:
    """
    UnlockHashCondition class
    """
    def __init__(self, unlockhash):
        """
        Initializes a new unlockhashcondition
        """
        self._unlockhash = unlockhash
