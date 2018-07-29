from jumpscale import j
from .ZeroOSFactory import ZeroOSFactory


JSBASE = j.application.jsbase_get_class()


class ZeroOSFactoryDeprecated(ZeroOSFactory, JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.clients.zero_os"
        JSBASE.__init__(self)
        self.logger.warning("`j.clients.zero_os` is deprecated, please use `j.clients.zos` instead")

        ZeroOSFactory.__init__(self)
