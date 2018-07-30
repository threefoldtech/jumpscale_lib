from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from .Zerobd import Zerobd

class ZerobdFactory(JSBASE):

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
        return Zerobd(node, name, path, mode, sync, admin, node_port)


