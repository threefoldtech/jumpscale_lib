from .ETCD import ETCD
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class ETCDFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.etcd"
        JSBASE.__init__(self)

    def get(self, node, name, password, data_dir='/mnt/data', zt_identity=None, nics=None, token=None, cluster=None):
        """
        Get sal for etcd management in ZOS

        Arguments:
            node: the node sal instance the etcd will be created on
            name: the name of the etcd instance
            password: password of the root user
            data_dir: etcd data directory
            zt_identity: zt identity of the etcd container
            nics: nics to be attached to the etcd container
            token: etcd cluster token
            cluster: all the cluster members. ex: [{'name': 'etcd_one', 'address': 'http://172.22.14.232:2380'}]

        Returns:
            the sal layer 
        """
        return ETCD(node, name, password, data_dir, zt_identity, nics, token, cluster)
