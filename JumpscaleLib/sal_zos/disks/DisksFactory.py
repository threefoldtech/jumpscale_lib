from .Disks import Disks
from Jumpscale import j

JSBASE = j.application.jsbase_get_class()


class DisksFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.disks"
        JSBASE.__init__(self)

    @staticmethod
    def get(node):
        """
        Get sal for Disks
        Returns:
            the sal layer 
        """
        return Disks(node)
