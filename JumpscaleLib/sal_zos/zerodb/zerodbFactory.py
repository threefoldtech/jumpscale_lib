from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from ..zerodb.zerodb import Zerodb, DEFAULT_PORT

class ZerodbFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.zos_sal.zerodb"
        JSBASE.__init__(self)

    def get(self, node, name, path=None, mode='user', sync=False, admin='', node_port=DEFAULT_PORT):
        """
        Get sal for Zerobd
        
        Arguments:
            node, name, path=None, mode='user', sync=False, admin='', node_port=DEFAULT_PORT
        
        Returns:
            the sal layer 
        """
        return Zerodb(node, name, path, mode, sync, admin, node_port)
