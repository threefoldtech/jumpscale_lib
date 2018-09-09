from Jumpscale import j

JSBASE = j.application.jsbase_get_class()

from .ETCD import ETCD


class ETCDFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.etcd"
        JSBASE.__init__(self)

    def get(
            self,
            name,
            container,
            serverBind,
            clientBind,
            peers,
            mgmtClientBind,
            data_dir='/mnt/data',
            password=None,
            logger=None):
        """
        Get sal for VM management in ZOS

        Arguments:
            name, container, serverBind, clientBind, peers, mgmtClientBind, data_dir,
            password, logger

        Returns:
            the sal layer
        """
        return ETCD(
            name,
            container,
            serverBind,
            clientBind,
            peers,
            mgmtClientBind,
            data_dir,
            password,
            logger)
