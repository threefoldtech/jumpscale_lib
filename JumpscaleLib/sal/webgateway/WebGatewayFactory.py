from Jumpscale import j

from .webgateway import WebGateway

JSConfigBaseFactory = j.tools.configmanager.JSBaseClassConfigs


class WebGatewayFactory(JSConfigBaseFactory):
    def __init__(self):
        self.__jslocation__ = "j.sal.webgateway"
        JSConfigBaseFactory.__init__(self, WebGateway)
