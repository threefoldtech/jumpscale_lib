from js9 import j
from .ZeroStorFactory import ZeroStorFactory


JSBASE = j.application.jsbase_get_class()


class ZeroStorFactoryDeprecated(ZeroStorFactory, JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.clients.zerostor"
        JSBASE.__init__(self)
        self.logger.warning("`j.clients.zerostor` is deprecated, please use `j.clients.zstor` instead")

        ZeroStorFactory.__init__(self)
