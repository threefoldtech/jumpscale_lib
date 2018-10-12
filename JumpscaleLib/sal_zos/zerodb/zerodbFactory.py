from Jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.JSBaseClass

from ..zerodb.zerodb import Zerodb

class ZerodbFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.zos_sal.zerodb"
        JSBASE.__init__(self)

    def get(self, node, name, path=None, mode='user', sync=False, admin=''):
        """
        Get sal for Zerobd
        
        Arguments:
            node, name, path=None, mode='user', sync=False, admin=''
        
        Returns:
            the sal layer 
        """
        return Zerodb(node, name, path, mode, sync, admin)
