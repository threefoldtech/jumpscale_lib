from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from .utils import Utils

class UtilsFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.utils"
        JSBASE.__init__(self)

    def get(self):
        """
        Get sal utilities
        
        """
        return Utils()


