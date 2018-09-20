from jumpscale import j

JSBASE = j.application.jsbase_get_class()

from .ETCD import ETCD, PEER_PORT, CLIENT_PORT

class ETCDFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.etcd"
        JSBASE.__init__(self)

    def get(self, node, name, listen_peer_urls=None, listen_client_urls=None, initial_advertise_peer_urls=None, advertise_client_urls=None, data_dir='/mnt/data', client_port=CLIENT_PORT, peer_port=PEER_PORT):
        """
        Get sal for etcd management in ZOS
        
        Arguments:
            node, name, listen_peer_urls, listen_client_urls, initial_advertise_peer_urls, advertise_client_urls, data_dir, client_port, peer_port
        
        Returns:
            the sal layer 
        """
        return ETCD(node, name, listen_peer_urls, listen_client_urls, initial_advertise_peer_urls, advertise_client_urls, data_dir, client_port, peer_port)