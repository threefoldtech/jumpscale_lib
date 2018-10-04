import time
import json
from jumpscale import j
from .. import templates
from ..abstracts import Nics, Service

logger = j.logger.get(__name__)
DEFAULT_PORT = 53

class Coredns(Service):
    """
    CoreDNS is a DNS server. It is written in Go
    """

    def __init__(self, name, node, etcd_endpoint, zt_identity=None, nics=None):
        super().__init__(name, node, 'coredns', [DEFAULT_PORT])
        self.name = name
        self.id = 'coredns.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.grid.tf/tf-official-apps/coredns-1.2.2.flist'
        self.etcd_endpoint = etcd_endpoint
        
        self._config_dir = '/usr/bin'
        self._config_name = 'coredns.conf'
        self.zt_identity = zt_identity
        self.nics = Nics(self)
        self.add_nics(nics)

    @property
    def _container_data(self):
        """
        :return: data used for coredns container
         :rtype: dict
        """
        ports = {
            str("{}|udp".format(DEFAULT_PORT)): DEFAULT_PORT,
        }
        self.authorize_zt_nics()

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'identity': self.zt_identity,
        }

    def deploy(self, timeout=120):
        # call the container property to make sure it gets created and the ports get updated
        self.container
        if not j.tools.timer.execute_until(lambda : self.container.mgmt_addr, timeout, 1):
            raise RuntimeError('Failed to get zt ip for etcd {}'.format(self.name))

    def create_config(self):
        logger.info('Creating coredns config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):

        return templates.render(
            'coredns.conf', etcd_ip =self.etcd_endpoint).strip()

    def start(self, timeout=15):
        """
        Start coredns
        :param timeout: time in seconds to wait for the coredns to start
        """
        if self.is_running():
            return

        logger.info('start coredns %s' % self.name)

        self.create_config()

        cmd = '/usr/bin/coredns -conf {dir}/{config}'.format(dir=self._config_dir,config=self._config_name)

        # wait for coredns to start
        self.container.client.system(cmd, id=self.id)
        if not j.tools.timer.execute_until(self.is_running, timeout, 0.5):
            raise RuntimeError('Failed to start CoreDns server: {}'.format(self.name))