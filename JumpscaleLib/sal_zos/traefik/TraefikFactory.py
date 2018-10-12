from .Traefik import Traefik
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class TraefikFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.traefik"
        JSBASE.__init__(self)

    def get(self, name, node, etcd_endpoint, etcd_watch=True,zt_identity=None, nics=None):
        """
        Get sal for traefik
        Returns:
            the sal layer 
        """
        return Traefik(name, node, etcd_endpoint, etcd_watch,zt_identity, nics)
