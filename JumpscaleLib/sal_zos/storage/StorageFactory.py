from .StoragePool import StoragePools
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class ContainerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.storagepools"
        JSBASE.__init__(self)

    def get(self, node):
        """
        Get sal for storage pools

        Arguments:
            node

        Returns:
            the sal layer 
        """
        return StoragePools(node)
