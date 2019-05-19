import json
import time

from jumpscale import j

from .. import templates
from ..abstracts import Nics, Service
from ..globals import TIMEOUT_DEPLOY

logger = j.logger.get(__name__)
DEFAULT_PORT = 53
EXPLORERS = ['"https://explorer.testnet.threefoldtoken.com"']


class CorednsThreebot(Service):
    """
    CoreDNS is a DNS server. It is written in Go
    """

    def __init__(self, name, node, zt_identity=None, nics=None, backplane='backplane', domain=None, explorers=None):
        super().__init__(name, node, 'coredns', [DEFAULT_PORT])
        self.name = name
        self.node = node
        self._container = None
        self.flist = 'https://hub.grid.tf/tf-autobuilder/threefoldtech-threebot_coredns-threebot_coredns-autostart-master.flist.md'
        self.domain = domain

        self._config_path = '/Corefile'
        self.zt_identity = zt_identity
        self.backplane = backplane
        self.nics = Nics(self)
        self.add_nics(nics)

        self.explorers = explorers

    @property
    def _container_data(self):
        """
        :return: data used for coredns container
         :rtype: dict
        """
        ports = {
            str("{}:{}|udp".format(self.backplane, DEFAULT_PORT)): DEFAULT_PORT,
        }
        self.authorize_zt_nics()

        data = {
            'name': self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'identity': self.zt_identity,
        }

        if self.explorers:
            data['config'] = {"/.startup.toml": self.get_coredns_config()}
        return data

    def deploy(self, timeout=TIMEOUT_DEPLOY):
        """create coredns container and get ZT ip

        Keyword Arguments:
            timeout {int} -- timeout of get ZeroTier IP (default: {120})
        """

        # call the container property to make sure it gets created and the ports get updated
        self.container
        if not j.tools.timer.execute_until(lambda: self.container.mgmt_addr, timeout, 1):
            raise RuntimeError('Failed to get zt ip for coredns {}'.format(self.name))

    def start(self, timeout=TIMEOUT_DEPLOY):
        """
        Start coredns
        :param timeout: time in seconds to wait for the coredns to start
        """
        if self.is_running():
            return

        logger.info('start coredns %s' % self.name)

        self.deploy()

    def get_coredns_config(self):
        return templates.render("corednsthreebot.conf", domain=self.domain, explorers=self.explorers)