from .Traefik import Traefik, DEFAULT_PORT
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class TraefikFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.traefik"
        JSBASE.__init__(self)

    @staticmethod
    def get(name, node, etcd_end_pint, node_port=DEFAULT_PORT, etcd_watch=True):
        """
        Get sal for traefik
        Returns:
            the sal layer 
        """
        return Traefik(name, node, node_port, etcd_end_pint, etcd_watch)
