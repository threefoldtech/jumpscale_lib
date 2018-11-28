from ..zerodb.zerodb import Zerodb
from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()


class ZerodbFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.zos_sal.zerodb"
        JSBASE.__init__(self)

    def get(self, node, name, node_port, path=None, mode='user', sync=False, admin=''):
        """
        Get sal for Zerobd

        Arguments:
            node, name, path=None, mode='user', sync=False, admin=''

        Returns:
            the sal layer
        """
        return Zerodb(node=node, name=name, node_port=node_port, path=path, mode=mode, sync=sync, admin=admin)
