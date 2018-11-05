from Jumpscale import j

from .webgateway import WebGateway

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class WebGatewayFactory(JSConfigBaseFactory):
    def __init__(self):
        self.__jslocation__ = "j.sal.webgateway"
        JSConfigBaseFactory.__init__(self, WebGateway)
