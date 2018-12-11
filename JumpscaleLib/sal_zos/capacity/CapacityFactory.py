from .Capacity import Capacity
from Jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.JSBaseClass


class CapacityFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.capacity"
        JSBASE.__init__(self)

    def get(self, node):
        """
        Get sal for Capacity

        Arguments:
            node

        Returns:
            the sal layer 
        """
        return Capacity(node)
