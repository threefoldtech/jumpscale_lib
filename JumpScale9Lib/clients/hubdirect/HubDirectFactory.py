from js9 import j
from .client import Client

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class HubDirectFactory(JSConfigBaseFactory):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.hubdirect"
        self.__imports__ = "ovc"
        JSConfigBaseFactory.__init__(self, Client)
