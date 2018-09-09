from .Minio import Minio, DEFAULT_PORT
from Jumpscale import j

JSBASE = j.application.jsbase_get_class()


class MinioFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.minio"
        JSBASE.__init__(self)

    @staticmethod
    def get(name, node, login, password, zdbs, namespace, private_key,
            namespace_secret='', node_port=DEFAULT_PORT, block_size=1048576,
            restic_username='', restic_password='', meta_private_key=''):
        """
        Get sal for minio
        Returns:
            the sal layer 
        """
        return Minio(name, node, login, password, zdbs, namespace, private_key,
                     namespace_secret, node_port, block_size, restic_username,
                     restic_password, meta_private_key)
