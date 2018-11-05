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
        self._frontends = {}
        self._backends = {}

    @property
    def etcd_client(self):
        if not self._etcd_client:
            self._etcd_client = j.clients.etcd.get(self._etcd_instance)
        return self._etcd_client

    @property
    def frontends(self):
        if not self._frontends:
            self._frontends, self._backends = encoding.load(self.etcd_client)
        return self._frontends

    @property
    def backends(self):
        if not self._backends:
            self._backends, self._backends = encoding.load(self.etcd_client)
        return self._backends

    def proxy_create(self, frontends, backends):
        return Proxy(self.etcd_client, frontends, backends)

    def frontend_create(self, name):
        if name in self._frontends:
            raise ValueError("a frontend names {} already exists".format(name))
        self._frontends[name] = Frontend(name)
        return self._frontends[name]

    def backend_create(self, name):
        if name in self._frontends:
            raise ValueError("a backend names {} already exists".format(name))
        self._backends[name] = Backend(name)
        return self._backends[name]


class Proxy:
    """
    The main class to use for adding/deleting reverse proxy forwarding into etcd
    """

    def __init__(self, etcd_client, frontends=None, backends=None):
        """
        :param etcd_client: etcd client instance (j.clients.etcd.get())
        """
        self.etcd_client = etcd_client
        self.frontends = frontends or []
        self.backends = backends or []

    def deploy(self):
        """
        add proxy configurations in etcd
        :param frontends: list of `Frontend` objects that needs to be added
        :param backends: list of `Backend` objects that will be connected to the frontend
        """
        for backend in self.backends:
            encoding.backend_delete(self.etcd_client, backend)
        for frontend in self.frontends:
            encoding.frontend_delete(self.etcd_client, frontend)

        # register the backends and frontends for traefik use
        for backend in self.backends:
            encoding.backend_write(self.etcd_client, backend)
        for frontend in self.frontends:
            encoding.frontend_write(self.etcd_client, frontend)

    def delete(self):
        """
        remove backends or frontends from etcd
        """
        backends = self.backends or []
        frontends = self.frontends or []

        for backend in backends:
            encoding.backend_delete(self.etcd_client, backend)

        for frontend in frontends:
            encoding.frontend_delete(self.etcd_client, frontend)

    def __repr__(self):
        out = "<Proxy>\n"
        for f in self.frontends:
            out += "  %s\n" % str(f)
        for b in self.backends:
            out += "  %s" % str(b)
        return out
