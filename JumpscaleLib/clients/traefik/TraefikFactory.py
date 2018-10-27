from Jumpscale import j

from .TraefikClient import (Backend, BackendServer, Frontend, FrontendRule,
                            TraefikClient)

JSConfigFactoryBase = j.tools.configmanager.JSBaseClassConfigs


class TraefikFactory(JSConfigFactoryBase):
    def __init__(self):
        self.__jslocation__ = "j.clients.traefik"
        JSConfigFactoryBase.__init__(self, TraefikClient)

    def configure(self, instance_name, host, port="2379", user="root", password="root"):
        """
        gets an instance of traefik client with etcd configurations directly
        """
        j.clients.etcd.get(instance_name, data={"host": host, "port": port, "user": user, "password_": password})
        return self.get(instance_name, data={"etcd_instance": instance_name})

    def test(self):
        cl = self.configure("test", host="10.102.64.236", user="root", password="v16ffehxnq")

        # create a first backend
        backend = cl.backend_create('backend1')
        server = backend.server_add('192.168.1.5:8080')
        server.weight = '20'

        # create a frontend
        frontend = cl.frontend_create('frontend1')
        # define the routing rule
        frontend.rule_add("my.domain.com")
        # link frontend1 to backend1
        frontend.backend_name = backend.name

        # create a proxy object. A proxy is a combinaison of frontends and backends
        proxy = cl.proxy_create([frontend], [backend])
        # write the configuration into etcd
        proxy.deploy()
        # delete all frontend and backend configuration of this proxy from etcd
        proxy.delete()
