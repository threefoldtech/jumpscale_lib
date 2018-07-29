from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from .Gateway import Gateway

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


