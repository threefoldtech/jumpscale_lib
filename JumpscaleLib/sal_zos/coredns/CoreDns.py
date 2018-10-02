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

    def __init__(self, name, node, etcd_endpoint, recursive_resolvers, zt_identity=None, nics=None):
        super().__init__(name, node, 'coredns', [DEFAULT_PORT])
        self.name = name
        self.id = 'coredns.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.grid.tf/tf-official-apps/coredns-1.2.2.flist'
        self.etcd_endpoint = etcd_endpoint
        self.node_port = None
        self.recursive_resolvers = "8.8.8.8:53 1.1.1.1:53"

        self._config_dir = '/usr/bin'
        self._config_name = 'coredns.conf'
        self.zt_identity = zt_identity
        self.nics = Nics(self)
        if nics:
            for nic in nics:
                nicobj = self.nics.add(nic['name'], nic['type'], nic['id'], nic.get('hwaddr'))
                if nicobj.type == 'zerotier':
                    nicobj.client_name = nic.get('ztClient')
        if 'nat0' not in self.nics:
            self.nics.add('nat0', 'default')


    @property
    def _container_data(self):
        """
        :return: data used for coredns container
         :rtype: dict
        """
        self.node_port = DEFAULT_PORT
        ports = {
            str("{}|udp".format(DEFAULT_PORT)): DEFAULT_PORT,
        }
        if not self.zt_identity:
            self.zt_identity = self.node.client.system('zerotier-idtool generate').get().stdout.strip()
        zt_public = self.node.client.system('zerotier-idtool getpublic {}'.format(self.zt_identity)).get().stdout.strip()
        j.sal_zos.utils.authorize_zerotiers(zt_public, self.nics)

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'identity': self.zt_identity,
        }

    def deploy(self):
        # call the container property to make sure it gets created and the ports get updated
        self.container
        for nic in self.nics:
            if nic.type == 'zerotier':
                zt_address = self.zt_identity.split(':')[0]
                try:
                    network = nic.client.network_get(nic.networkid)
                    member = network.member_get(address=zt_address)
                    member.timeout = None
                    member.get_private_ip(60)
                except (RuntimeError, ValueError) as e:
                    logger.warning('Failed to retreive zt ip: %s', str(e))

    def create_config(self):
        logger.info('Creating coredns config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):

        return templates.render(
            'coredns.conf', etcd_ip =self.etcd_endpoint).strip()

    def is_running(self):
        try:
            for _ in self.container.client.job.list(self.id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def start(self, timeout=15):
        """
        Start coredns
        :param timeout: time in seconds to wait for the coredns to start
        """
        is_running = self.is_running()
        if is_running:
            return

        logger.info('start coredns %s' % self.name)

        self.create_config()

        cmd = '/usr/bin/coredns -conf {dir}/{config}'.format(dir=self._config_dir,config=self._config_name)

        # wait for coredns to start
        self.container.client.system(cmd, id=self.id)
        if j.tools.timer.execute_until(self.is_running, timeout, 0.5):
            return True

        if not is_running:
            raise RuntimeError('Failed to start coredns server: {}'.format(self.name))

    def stop(self, timeout=30):
        """
        Stop the coredns
        :param timeout: time in seconds to wait for the coredns gateway to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.info('stop coredns %s' % self.name)

        self.container.client.job.kill(self.id)

        # wait for coredns to stop
        if j.tools.timer.execute_until(self.is_running, timeout, 0.5):
            return True

        if is_running:
            raise RuntimeError('Failed to stop coredns server: {}'.format(self.name))

        self.container.stop()

    def destroy(self):
        self.stop()
        self.container.stop()
