from .IPPoolManager import IPPoolsManager
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class IPPoolManagerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.ippoolmanager"
        JSBASE.__init__(self)

    def get(self, pools):
        """
        Get sal for ippoolmanager

        Returns:
            the sal layer 
        """
        return IPPoolsManager(pools)
