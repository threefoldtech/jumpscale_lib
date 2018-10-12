import time
from Jumpscale import j
from .. import templates
from ..abstracts import Nics, Service

logger = j.logger.get(__name__)
DEFAULT_PORT_HTTP = 80
DEFAULT_PORT_HTTPS = 443


class Traefik(Service):
    """
    Traefik a modern HTTP reverse proxy
    """

    def __init__(self, name, node, etcd_endpoint, etcd_watch=True, zt_identity=None, nics=None):
        super().__init__(name, node, 'traefik', [DEFAULT_PORT_HTTP, DEFAULT_PORT_HTTPS])
        self.name = name
        self.id = 'traefik.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.grid.tf/tf-official-apps/traefik-v1.7.0-rc5.flist'
        self.etcd_endpoint = etcd_endpoint
        self.etcd_watch = etcd_watch
        self.node_port = None

        self._config_dir = '/usr/bin'
        self._config_name = 'traefik.toml'
        self.zt_identity = zt_identity
        self.nics = Nics(self)
        self.add_nics(nics)

    @property
    def _container_data(self):
        """
        :return: data used for traefik container
         :rtype: dict
        """
        self.node_port = DEFAULT_PORT_HTTP
        ports = {
            str(DEFAULT_PORT_HTTP): DEFAULT_PORT_HTTP,
            str(DEFAULT_PORT_HTTPS): DEFAULT_PORT_HTTPS,  # HTTPS
        }
        self.authorize_zt_nics()

        return {
            'name':  self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'identity': self.zt_identity,
        }

    def deploy(self, timeout=120):
        """create traefik contianer and get ZT ip

        Keyword Arguments:
            timeout {int} -- timeout of get ZeroTier IP (default: {120})
        """

        # call the container property to make sure it gets created and the ports get updated
        self.container
        if not j.tools.timer.execute_until(lambda: self.container.mgmt_addr, timeout, 1):
            raise RuntimeError('Failed to get zt ip for traefik {}'.format(self.name))

    def container_port(self, port):

        return self._container.get_forwarded_port(port)

    def create_config(self):
        """
        create configuration of traefik and upload it in the container
        """
        logger.info('Creating traefik config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):
        """
        render traefik config template using etcd ip, user, password
        and add key of SSL certificate to etcd
        """

        # for SSL Certifcate
        client = j.clients.etcd.get(self.name, data={'host': self.etcd_endpoint['ip'], 'port': self.etcd_endpoint['client_port'],
                                                     'password_': self.etcd_endpoint['password'], 'user': "root"})
        client.put("traefik/acme/account", "")
        return templates.render(
            'traefik.conf', etcd_ip='{}:{}'.format(self.etcd_endpoint['ip'], self.etcd_endpoint['client_port']), user="root", passwd=self.etcd_endpoint['password']).strip()

    def start(self, timeout=120):
        """
        Start traefik
        store config in etcd
        :param timeout: time in seconds to wait for the traefik to start
        """
        if self.is_running():
            return

        logger.info('start traefik %s' % self.name)

        self.create_config()

        cmd = '/usr/bin/traefik storeconfig -c {dir}/{config}'.format(dir=self._config_dir, config=self._config_name)
        job = self.container.client.system(cmd, id=self.id)
        cmd = '/usr/bin/traefik -c {dir}/{config}'.format(dir=self._config_dir, config=self._config_name)

        # wait for traefik to start
        self.container.client.system(cmd, id=self.id)
        if not j.tools.timer.execute_until(self.is_running, timeout, 0.5):
            result = job.get()
            raise RuntimeError('Failed to start Traefik server {}: {}'.format(self.name, result.stderr))
