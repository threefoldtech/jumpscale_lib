from .ZOS_VM import ZOS_VM
from Jumpscale import j
JSBASE = j.application.JSBaseClass


class ZOS_VMFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.vm"
        JSBASE.__init__(self)

    @staticmethod
    def get(node, name, flist=None, vcpus=2, memory=2048):
        """
        Get sal for VM management in ZOS

        Returns:
            the sal layer 
        """
        return ZOS_VM(node, name, flist, vcpus, memory)
