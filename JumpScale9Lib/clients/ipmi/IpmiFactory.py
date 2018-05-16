from .Ipmi import Ipmi

from js9 import j

JSConfigBaseFactory = j.tools.configmanager.base_class_configs

class IYOFactory(JSConfigBaseFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.ipmi"
        JSConfigBaseFactory.__init__(self, Ipmi)
