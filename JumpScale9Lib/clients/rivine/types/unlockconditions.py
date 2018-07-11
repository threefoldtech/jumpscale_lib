"""
Unlockconditions module
"""

from JumpScale9Lib.clients.rivine.encoding import binary
from JumpScale9Lib.clients.rivine.errors import DoubleSignatureError
from JumpScale9Lib.clients.rivine.types.unlockhash import UnlockHash

# this is the value if the locktime is less than it, it means that the locktime should be interpreted as the chain height lock instead of the timestamp
TIMELOCK_CONDITION_HEIGHT_LIMIT = 5000000
ATOMICSWAP_CONDITION_TYPE = bytearray([2])


class BaseFulFillment:
    """
    BaseFulFillment class
    """
    def __init__(self, pub_key):
        """
        Initializes a new BaseFulfillment object
        """
        self._pub_key = pub_key
        self._signature = None
        self._extra_objects = None


    @property
    def json(self):
        """
        Returns a json encoded versoin of the Fulfillment
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
        sig_hash = sig_ctx['transaction'].get_input_signature_hash(input_index=sig_ctx['input_idx'],
                                                                    extra_objects=self._extra_objects)
        self._signature = sig_ctx['secret_key'].sign(sig_hash)




class AtomicSwapFulfillment(BaseFulFillment):
    """
    AtomicSwapFulfillment class
    """
    def __init__(self, pub_key, secret=None):
        """
        Initializes a new AtomicSwapFulfillment object
        """
        super().__init__(pub_key=pub_key)
        self._secret = secret
        self._type = bytearray([2])
        self._extra_objects = [self._pub_key]
        if self._secret is not None:
            self._extra_objects.append(bytearray.fromhex(self._secret))


    @property
    def json(self):
        """
        Returns a json encoded versoin of the SingleSignatureFulfillment
        """
        result = super().json
        if self._secret:
            result['data']['secret'] = self._secret
        return result



class SingleSignatureFulfillment(BaseFulFillment):
    """
    SingleSignatureFulfillment class
    """
    def __init__(self, pub_key):
        """
        Initialzies new single singnature fulfillment class
        """
        super().__init__(pub_key=pub_key)
        self._type = bytearray([1])




class AtomicSwapCondition:
    """
    AtomicSwapCondition class
    """
    def __init__(self, sender, reciever, hashed_secret, locktime):
        """
        Initializes a new AtomicSwapCondition object
        """
        self._sender = sender
        self._reciever = reciever
        self._hashed_secret = hashed_secret
        self._locktime = locktime
        self._type = ATOMICSWAP_CONDITION_TYPE


    @property
    def binary(self):
        """
        Returns a binary encoded versoin of the AtomicSwapCondition
        """
        result = bytearray()
        result.extend(self._type)
        # 106 size of the atomicswap condition in binary form
        result.extend(binary.encode(106))
        result.extend(binary.encode(UnlockHash.from_string(self._sender)))
        result.extend(binary.encode(UnlockHash.from_string(self._reciever)))
        result.extend(binary.encode(self._hashed_secret, type_='hex'))
        result.extend(binary.encode(self._locktime))

        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the AtomicSwapCondition
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'timelock': self._locktime,
                'sender': self._sender,
                'receiver': self._reciever,
                'hashedsecret': self._hashed_secret
            }
        }



class LockTimeCondition:
    """
    LockTimeCondition class
    """
    def __init__(self, condition, locktime):
        """
        Initializes a new LockTimeCondition

        @param locktime: Identifies the height or timestamp until which this output is locked
        If the locktime is less then 500 milion it is to be assumed to be identifying a block height,
        otherwise it identifies a unix epoch timestamp in seconds

        @param condition: A condtion object that can be an UnlockHashCondition or a MultiSignatureCondition
        """
        self._locktime = int(locktime)
        self._condition = condition
        self._type = bytearray([3])



    @property
    def binary(self):
        """
        Returns a binary encoded versoin of the LockTimeCondition
        """
        result = bytearray()
        result.extend(self._type)
        # encode the length of all properties: len(locktime) = 8 + len(binary(condition)) - 8
        # the -8 in the above statement is due to the fact that we do not need to include the length of the interal condition's data
        result.extend(binary.encode(len(self._condition.binary)))
        result.extend(binary.encode(self._locktime))
        result.extend(self._condition.type)
        result.extend(binary.encode(self._condition.data))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the LockTimeCondition
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'locktime': self._locktime,
                'condition': self._condition.json
            }
        }



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
    def type(self):
        """
        Returns the unlock type
        """
        return self._type


    @property
    def data(self):
        """
        Returns the condtion data being the unlockhash in this condition type
        """
        return self._unlockhash


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
