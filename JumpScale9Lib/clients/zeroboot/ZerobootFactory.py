import os

from js9 import j

from .ZerobootClient import ZerobootClient
JSConfigFactoryBase = j.tools.configmanager.base_class_configs

class ZeroRobotFactory(JSConfigFactoryBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zboot"
        JSConfigFactoryBase.__init__(self, ZerobootClient)
