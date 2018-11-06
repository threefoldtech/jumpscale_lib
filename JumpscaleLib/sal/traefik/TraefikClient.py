from jumpscale import j

from . import encoding
from .types import (Backend, BackendServer, Frontend, FrontendRule,
                    LoadBalanceMethod, RoutingKind)

JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
etcd_instance = "main"
"""


class TraefikClient(JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self._etcd_client = None
        self._etcd_instance = self.config.data['etcd_instance']
        self._proxies = []
        self._frontends = {}
        self._backends = {}

    @property
    def etcd_client(self):
        if not self._etcd_client:
            self._etcd_client = j.clients.etcd.get(self._etcd_instance)
        return self._etcd_client

    def proxy_create(self, name):
        """
        create a new reverse proxy

        :param name: name of your proxy, it needs to be unique inside the etcd cluster
        :type name: string
        :return: Proxy object
        :rtype: JumpscaleLib.sal.traefik.TraefikClient.Proxy
        """

        return Proxy(self.etcd_client, name)

    @property
    def proxies(self):
        """
        list all the proxies that exists

        :return: list of proxy object
        :rtype: list
        """

        if not self._proxies:
            frontends, backends = encoding.load(self.etcd_client)
            for frontend in frontends.values():
                proxy = Proxy(self.etcd_client, name=frontend.name, frontend=frontend, backend=backends.get(frontend.backend_name))
                self._proxies.append(proxy)
        return self._proxies


class Proxy:
    """
    The main class to use for adding/deleting reverse proxy forwarding into etcd
    """

    def __init__(self, etcd_client, name, frontend=None, backend=None):
        """
        :param etcd_client: etcd client instance (j.clients.etcd.get())
        """
        self.etcd_client = etcd_client
        self.name = name
        self.frontend = frontend
        self.backend = backend

    def frontend_set(self, domain):
        """
        set a frontend on the proxy.
        The frontend will redirect requests coming to domain to the backend of this proxy

        :param domain: domain name
        :type domain: str
        :return: return a frontend object on which you can fine tune the frontend routing rules
        :rtype: JumpscaleLib.sal.traefik.types.Frontend
        """

        # remove previous frontend if any
        if self.frontend:
            encoding.frontend_delete(self.etcd_client, self.frontend)

        self.frontend = Frontend(name=self.name, backend_name=self.name)
        self.frontend.rule_add(domain)
        return self.frontend

    def backend_set(self, endpoints=None):
        """
        set a backend on the proxy.
        The backend will receive all the equests coming to domain configured in the frontend of this proxy

        :param endpoints: if provided, a list of url to the backend servers
        :type endpoints: list
        :return: return a backend object on which you can configure more backend server
        :rtype: JumpscaleLib.sal.traefik.types.Backend
        """
        # remove previous backend if any
        if self.backend:
            encoding.backend_delete(self.etcd_client, self.backend)

        if not isinstance(endpoints, list):
            endpoints = [endpoints]

        self.backend = Backend(self.name)
        for endpoint in endpoints or []:
            self.backend.server_add(endpoint)
        return self.backend

    def deploy(self):
        """
        write the configuration of this proxy to etcd
        """
        # register the backends and frontends for traefik use
        if self.backend:
            encoding.backend_write(self.etcd_client, self.backend)
        if self.frontend:
            encoding.frontend_write(self.etcd_client, self.frontend)

    def delete(self):
        """
        remove backends or frontends from etcd
        """
        if self.backend:
            encoding.backend_delete(self.etcd_client, self.backend)
        if self.frontend:
            encoding.frontend_delete(self.etcd_client, self.frontend)

        self.backend = None
        self.frontend = None

    def __repr__(self):
        return "<Proxy> %s" % self.name
