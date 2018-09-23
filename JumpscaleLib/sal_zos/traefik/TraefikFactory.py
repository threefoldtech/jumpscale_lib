from .Traefik import Traefik
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class TraefikFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.traefik"
        JSBASE.__init__(self)

    @staticmethod
    def get(name, node, etcd_end_pint, etcd_watch=True):
        """
        Get sal for traefik
        Returns:
            the sal layer 
        """
        return Traefik(name, node, etcd_end_pint, etcd_watch)
