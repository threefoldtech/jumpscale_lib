from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from .ZOS_VM import ZOS_VM

class ZOS_VMs(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.vm"
        JSBASE.__init__(self)

    def get(self, data):
        """
        Get sal for VM management in ZOS
        
        Arguments:
            object using jumpscale schema
        
        Returns:
            the sal layer 
        """
        return ZOS_VM(data)

    def dataobj_new(self):
        """
        """
        

