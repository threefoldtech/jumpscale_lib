import time

from Jumpscale import j

from .Client import Client

JSConfigFactoryBase = j.tools.configmanager.JSBaseClassConfigs
logger = j.logging.get(__name__)


class ZeroOSFactory(JSConfigFactoryBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zos_protocol"
        super().__init__(Client)
        self.connections = {}        