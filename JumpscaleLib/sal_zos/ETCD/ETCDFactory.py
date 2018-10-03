from jumpscale import j

JSBASE = j.application.jsbase_get_class()

from .ETCD import ETCD

class ETCDFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.etcd"
        JSBASE.__init__(self)

    def get(self, node, name, data_dir='/mnt/data', zt_identity=None, nics=None, token=None, cluster=None):
        """
        Get sal for etcd management in ZOS
        
        Arguments:
            node, name, data_dir, zt_identity, nics, token, cluster
        
        Returns:
            the sal layer 
        """
        return ETCD(node, name, data_dir, zt_identity, nics, token, cluster)