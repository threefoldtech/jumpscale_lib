from ..gateway.gateway import Gateway
from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()


class GatewayFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.zos_sal.gateway"
        JSBASE.__init__(self)

    def get(self, node, name):
        """
        Get sal for Gateway

        Arguments:
            node
            name

        Returns:
            the sal layer 
        """
        return Gateway(node, name)
