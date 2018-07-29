from jumpscale import j

JSBASE = j.application.jsbase_get_class()

from .Container import Containers

class ContainerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.containers"
        JSBASE.__init__(self)

    def get(self, node):
        """
        Get sal for VM management in ZOS
        
        Arguments:
            node
        
        Returns:
            the sal layer 
        """
        return Containers(node)