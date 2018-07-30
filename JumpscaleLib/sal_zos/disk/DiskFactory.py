from jumpscale import j

JSBASE = j.application.jsbase_get_class()

from .Disk import Disks

class DiskFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.disks"
        JSBASE.__init__(self)

    def get(self, node):
        """
        Get sal for VM management in ZOS
        
        Arguments:
            node
        
        Returns:
            the sal layer 
        """
        return Disks(node)