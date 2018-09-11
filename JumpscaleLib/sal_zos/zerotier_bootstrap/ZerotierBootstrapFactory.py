from Jumpscale import j
JSBASE = j.application.JSBaseClass

from .ZerotierBootstrap import ZTBootstrap


class ZerotierBootstrapFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.zt_bootstrap"
        JSBASE.__init__(self)

    def get(self, zt_token, bootstap_id, grid_id, cidr):
        """
        Get sal for zerotier bootstrap in ZOS
        Returns:
            the sal layer
        """
        return ZTBootstrap(zt_token, bootstap_id, grid_id, cidr)
