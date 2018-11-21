from jumpscale import j

from .ZeroTierController import ZeroTierController

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class TraefikFactory(JSConfigBaseFactory):
    def __init__(self):
        self.__jslocation__ = "j.sal.zerotier_Controller"
        JSConfigBaseFactory.__init__(self, ZeroTierController)