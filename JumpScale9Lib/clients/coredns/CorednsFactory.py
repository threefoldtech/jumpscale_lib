from js9 import j

JSConfigBase = j.tools.configmanager.base_class_configs

from .CorednsClient import CorednsClient

class CorednsFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.coredns"
        JSConfigBase.__init__(self, CorednsClient)