from Jumpscale import j
from .TraefikClient import TraefikClient
JSConfigFactoryBase = j.tools.configmanager.JSBaseClassConfigs


class TraefikFactory(JSConfigFactoryBase):
    def __init__(self):
        self.__jslocation__ = "j.clients.traefik"
        JSConfigFactoryBase.__init__(self, TraefikClient)

    def config_get(self, instance_name, host, port="2379", user="root", password="root"):
        """
        gets an instance of traefik client with etcd configurations directly
        """
        j.clients.etcd.get(instance_name, data={"host": host, "port": port, "user": user, "password_": password})
        return self.get(instance_name, data={"etcd_instance": instance_name})

    def test(self):
        cl = self.config_get("test", host="10.102.64.236", user="root", password="v16ffehxnq")
        frontendrule = cl.frontend_rule_get("www.test.com")
        backendserver = cl.backend_server_get("0.0.0.0")
        backends = [cl.backend_get("backend1", servers=[backendserver]),
                    cl.backend_get("backend2", servers=[backendserver])]

        frontends = [cl.frontend_get("frontend1", "backend1", rules=[frontendrule]),
                     cl.frontend_get("frontend2", "backend2", rules=[frontendrule])]

        cl.proxy.deploy(frontends=frontends, backends=backends)
        cl.proxy.delete(frontends=frontends, backends=backends)
        j.shell()
