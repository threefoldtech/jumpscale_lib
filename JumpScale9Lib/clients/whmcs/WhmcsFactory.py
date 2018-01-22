from js9 import j
from JumpScale9Lib.clients.whmcs.WhmcsInstance import WhmcsInstance

JSConfigFactory = j.tools.configmanager.base_class_configs
class Dummy:

    def __getattribute__(self, attr, *args, **kwargs):
        def dummyFunction(*args, **kwargs):
            pass
        return dummyFunction

    def __setattribute__(self, attr, val):
        pass


class DummyWhmcs:

    def __init__(self):
        self.tickets = Dummy()
        self.orders = Dummy()
        self.users = Dummy()


class WhmcsFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.whmcs"
        self.logger = j.logger.get('j.clients.whmcs')
        JSConfigFactory.__init__(self, WhmcsInstance)

    def getDummy(self):
        return DummyWhmcs()
