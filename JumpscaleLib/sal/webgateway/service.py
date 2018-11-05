from io import StringIO
from urllib.parse import urlparse

from jumpscale import j
from JumpscaleLib.sal.coredns.ResourceRecord import RecordType


class Service:

    def __init__(self, name, public_ips, traefik, coredns):
        self.name = name
        self.public_ips = public_ips
        self._traefik = traefik
        self._coredns = coredns
        self.proxy = self._load_proxy()

    def _load_proxy(self):
        frontend = None
        backend = None
        for f in self._traefik.frontends.values():
            if f.name == self.name:
                frontend = f
                break

        for b in self._traefik.backends.values():
            if b.name == self.name:
                backend = b
                break

        if not frontend or not backend:
            return

        if frontend.backend_name != backend.name:
            raise RuntimeError()
        return self._traefik.proxy_create([frontend], [backend])

    def _deploy_dns(self, domain):
        for ip in self.public_ips:
            self._coredns.zone_create(domain, ip)

    def _deploy_reverse_proxy(self, domain, endpoints):
        if self.name in self._traefik.backends:
            backend = self._traefik.backends[self.name]
        else:
            backend = self._traefik.backend_create(self.name)

        for endpoint in endpoints:
            u = urlparse(endpoint)
            if not all([u.hostname, u.port, u.scheme]):
                raise ValueError("wrong format for endpoint %s" % endpoint)
            server = backend.server_add(url=endpoint, weight=10)  # TODO: allow to set weight

        if self.name in self._traefik.frontends:
            frontend = self._traefik.frontends[self.name]
        else:
            frontend = self._traefik.frontend_create(self.name)

        if len(frontend.rules) <= 0:
            frontend.rule_add(domain)
        else:
            rule = frontend.rules[0]
            existing_domains = rule.value.split(',')
            if domain not in existing_domains:
                rule.value += ',%s' % domain

        frontend.backend_name = backend.name

        proxy = self._traefik.proxy_create([frontend], [backend])
        self.proxy = proxy

    def expose(self, domain, endpoints):
        """
        High level method to easily expose a service over a domain

        This method will do 2 things:
        1. configure coredns to handle the domain and point it to the public of the webgateway
        2. configure traefik to create a reverse proxy from the domain to all the endpoints

        :param domain: domain name you want to use to expose your service
        :type domain: str
        :param endpoints: list of URL used by the reverse proxy needs to use as backend
        :type endpoints: [str]
        """

        self._deploy_dns(domain)
        self._deploy_reverse_proxy(domain, endpoints)
        self.deploy()

    def deploy(self):
        """
        write all the configuration of the service to etcd
        use this method when you have manually change some configuration of the service
        and want to make it reality by writting it into etcd
        """
        if self.proxy:
            self.proxy.deploy()
        if self._coredns:
            self._coredns.deploy()

    def delete(self):
        """
        delete all trace from this service from etcd

        it will remove all traefik and all coredns configuration
        """

        if self.proxy:
            self.proxy.delete()
        # if self._coredns: TODO
        #     self._coredns.deploy()

    def summary(self):
        """
        helper method to print a summary of the configuration of your service
        :return: printable representation of the service
        :rtype: str
        """

        buf = StringIO()
        buf.write("Service %s\n" % self.name)
        if self.proxy:
            buf.write("frontends:\n")
            for frontend in self.proxy.frontends:
                for rule in frontend.rules:
                    buf.write("  %s\n" % rule.value)
            buf.write("backends:\n")
            for backend in self.proxy.backends:
                for server in backend.servers:
                    buf.write("  %s://%s:%s\n" % (server.scheme, server.ip, server.port))
        return buf.getvalue()

    def __repr__(self):
        return "<WebGateway Service> %s" % self.name
