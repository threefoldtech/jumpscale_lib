from .CoreDns import Coredns
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class CorednsFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.coredns"
        JSBASE.__init__(self)

    @staticmethod
    def get(name, node, etcd_endpoint, recursive_resolvers ="8.8.8.8:53 1.1.1.1:53", zt_identity=None, nics=None):
        """
        Get sal for coredns
        Returns:
            the sal layer 
        """
        return Coredns(name, node, etcd_endpoint, recursive_resolvers, zt_identity, nics)
