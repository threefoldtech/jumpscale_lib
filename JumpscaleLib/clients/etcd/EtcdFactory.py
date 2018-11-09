from Jumpscale import j
from .EtcdClient import EtcdClient


JSConfigFactory = j.tools.configmanager.JSBaseClassConfigs


class EtcdFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.etcd"
        JSConfigFactory.__init__(self, EtcdClient)
