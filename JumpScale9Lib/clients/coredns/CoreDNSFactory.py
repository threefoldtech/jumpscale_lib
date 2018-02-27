
from js9 import j

JSBASE = j.application.jsbase_get_class()

from .CoreDNSClient import *

JSConfigBase = j.tools.configmanager.base_class_configs



class CoreDNSFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.coredns"
        JSConfigBase.__init__(self, CoreDNSClient)

    def get_by_params(self, instance="main", redisname="coredns"):
        """
        name of redis connection
        get as follows:

        j.clients.redis_config.get_by_params(instance='coredns', ipaddr='localhost', port=6380, password='', unixsocket='', ardb_patch=False)

        """
        data = {}
        data["redisconfigname"] = redisname
        return self.get(instance=instance, data=data)

    def test(self):
        redis = j.clients.redis_config.get_by_params(instance="coredns",port=6380)
        cl = self.get_by_params(redis.instance)
        cl.record_a_set("test.something","192.168.8.8")

        #use dns python tools to connect to the coredns server over port 53 and test all the records 
        j.tools.dnstools

        #TODO:*1
