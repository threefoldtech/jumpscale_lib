import time
from jumpscale import j
from .. import templates


logger = j.logger.get(__name__)
DEFAULT_PORT = 9500

class Coredns:
    """
    CoreDNS is a DNS server. It is written in Go
    """

    def __init__(self, name, node, etcd_endpoint, domain, recursive_resolvers):
        
        self.name = name
        self.id = 'coredns.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.grid.tf/tf-official-apps/coredns-1.2.2.flist'
        self.etcd_endpoint = etcd_endpoint
        self.domain = domain
        self.node_port = None
        self.recursive_resolvers = recursive_resolvers

        self._config_dir = '/usr/bin'
        self._config_name = 'coredns.conf'

    @property
    def _container_data(self):
        """
        :return: data used for coredns container
         :rtype: dict
        """
        ports = self.node.freeports(1)
        if len(ports) <= 0:
            raise RuntimeError("can't install coredns, no free port available on the node")

        self.node_port = ports[0]
        ports = {
            str(ports[0]): self.node_port,
        }
        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [{'type': 'default'}],
        }

    @property
    def _container_name(self):
        """
        :return: name used for coredns container
        :rtype: string
        """
        return 'coredns_{}'.format(self.name)

    @property
    def container(self):
        """
        Get/create coredns container to run coredns services on
        :return: coredns container
        :rtype: container sal object
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self._container_name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data)
        return self._container

    def create_config(self):
        logger.info('Creating coredns config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):

        return templates.render(
            'coredns.conf', etcd_ip =self.etcd_endpoint, domain=self.domain, recursive_resolvers=self.recursive_resolvers).strip()

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

        cmd = '/usr/bin/coredns ./coredns  -conf {dir}/{config}'.format(dir=self._config_dir,config=self._config_name)

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

    
    
