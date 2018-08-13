import time

from jumpscale import j

from .Client import Client

JSConfigFactoryBase = j.tools.configmanager.base_class_configs
logger = j.logging.get(__name__)


class ZeroOSFactory(JSConfigFactoryBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zos_protocol"
        super().__init__(Client)
        self.connections = {}        