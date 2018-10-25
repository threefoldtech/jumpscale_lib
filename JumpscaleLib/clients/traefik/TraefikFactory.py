from Jumpscale import j
from .TraefikClient import TraefikClient
JSConfigFactoryBase = j.tools.configmanager.JSBaseClassConfigs


class TraefikFactory(JSConfigFactoryBase):
    def __init__(self):
        self.__jslocation__ = "j.clients.traefik"
        JSConfigFactoryBase.__init__(self, TraefikClient)
