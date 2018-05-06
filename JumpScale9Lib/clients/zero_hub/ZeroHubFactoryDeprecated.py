from js9 import j
from .ZeroHubFactory import ZeroHubFactory


JSBASE = j.application.jsbase_get_class()


class ZeroHubFactoryDeprecated(ZeroHubFactory, JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.clients.zerohub"
        JSBASE.__init__(self)
        self.logger.warning("`j.clients.zerohub` is deprecated, please use `j.clients.zhub` instead")

        ZeroHubFactory.__init__(self)
