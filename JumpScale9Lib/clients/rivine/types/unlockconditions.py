"""
Unlockconditions module
"""

from JumpScale9Lib.clients.rivine.errors import DoubleSignatureError
from JumpScale9Lib.clients.rivine.encoding import binary

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
        self._type = bytearray([1])


    @property
    def json(self):
        """
        Returns a json encoded versoin of the SingleSignatureFulfillment
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data':{
                'publickey': self._pub_key.json,
                'signature': self._signature.hex() if self._signature else ''
            }
        }


    def sign(self, sig_ctx):
        """
        Sign the given fulfillment, which is to be done after all properties have been filled of the parent transaction

        @param sig_ctx: Signature context should be a dictionary containing the secret key, input index, and transaction object
        """
        if self._signature is not None:
            raise DoubleSignatureError("cannot sign a fulfillment which is already signed")
        sig_hash = sig_ctx['transaction'].get_input_signature_hash(input_index=sig_ctx['input_idx'])
        self._signature = sig_ctx['secret_key'].sign(sig_hash)



class TimeLockCondition:
    """
    TimeLockCondition class
    """
    def __init__(self, locktime, condition):
        """
        Initializes a new TimeLockCondition

        @param locktime: Identifies the height or timestamp until which this output is locked
        If the locktime is less then 500 milion it is to be assumed to be identifying a block height,
        otherwise it identifies a unix epoch timestamp in seconds

        @param condition: A condtion object that can be an UnlockHashCondition or a MultiSignatureCondition
        """
        self._locktime = locktime
        self._condition = condition



class UnlockHashCondition:
    """
    UnlockHashCondition class
    """
    def __init__(self, unlockhash):
        """SingleSignatureFulfillment
        Initializes a new unlockhashcondition
        """
        self._unlockhash = unlockhash
        self._type = bytearray([1])
        self._unlockhash_size = 33



    @property
    def binary(self):
        """
        Returns a binary encoded version of the unlockhashcondition
        """
        result = bytearray()
        result.extend(self._type)
        # add the size of the unlockhash
        result.extend(binary.encode(self._unlockhash_size))
        result.extend(binary.encode(self._unlockhash))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the UnlockHashCondition
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'unlockhash': str(self._unlockhash)
            }
        }
