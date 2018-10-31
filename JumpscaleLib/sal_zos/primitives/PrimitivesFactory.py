from .Primitives import Primitives
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class PrimitivesFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.primitives"
        JSBASE.__init__(self)

    @staticmethod
    def get(node):
        """
        Get sal for zos primitives
        Returns:
            the sal layer 
        """
        return Primitives(node)

