from .Hypervisor import Hypervisor
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class HypervisorFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.hypervisor"
        JSBASE.__init__(self)

    @staticmethod
    def get(node):
        """
        Get sal for Hypervisor
        Returns:
            the sal layer 
        """
        return Hypervisor(node)
