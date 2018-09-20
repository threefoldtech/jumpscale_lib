import time
from jumpscale import j
from .. import templates


logger = j.logger.get(__name__)
DEFAULT_PORT = 9700

class Traefik:
    """
    Traefik a modern HTTP reverse proxy
    """

    def __init__(self, name, node, etcd_end_pint, node_port=DEFAULT_PORT, etcd_watch=True):
        
        self.name = name
        self.id = 'traefik.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.gig.tech/delandtj/traefik.flist'
        self.node_port = node_port
        self.etcd_end_pint =etcd_end_pint
        self.etcd_watch = etcd_watch

        self._config_dir = '/bin'
        self._config_name = 'traefik.toml'

    @property
    def _container_data(self):
        """
        :return: data used for traefik container
         :rtype: dict
        """
        ports = self.node.freeports(self.node_port, 1)
        if len(ports) <= 0:
            raise RuntimeError("can't install traefik, no free port available on the node")

        self.node_port = ports[0]

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': {self.node_port: DEFAULT_PORT},
            'nics': [{'type': 'default'}],
        }

    @property
    def _container_name(self):
        """
        :return: name used for traefik container
        :rtype: string
        """
        return 'traefik_{}'.format(self.name)

    @property
    def container(self):
        """
        Get/create traefik container to run traefik services on
        :return: traefik container
        :rtype: container sal object
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self._container_name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data)
        return self._container

    def create_config(self):
        logger.info('Creating traefik config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):

        return templates.render(
            'traefik.conf', etcd_ip =self.etcd_end_pint, etcd_Watch = self.etcd_watch).strip()

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
        Start traefik
        :param timeout: time in seconds to wait for the traefik to start
        """
        is_running = self.is_running()
        if is_running:
            return

        logger.info('start traefik %s' % self.name)

        self.create_config()

        cmd = '/bin/traefik ./traefik  -c {dir}'.format(dir=self._config_dir)

        # wait for traefik to start
        self.container.client.system(cmd, id=self.id)
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if not is_running:
            raise RuntimeError('Failed to start traefik server: {}'.format(self.name))

        self.container.node.client.nft.open_port(self.node_port)

    def stop(self, timeout=30):
        """
        Stop the traefik
        :param timeout: time in seconds to wait for the traefik gateway to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.info('stop traefik %s' % self.name)

        self.container.client.job.kill(self.id)

        # wait for traefik to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if is_running:
            raise RuntimeError('Failed to stop traefik server: {}'.format(self.name))

        self.container.node.client.nft.drop_port(self.node_port)
        self.container.stop()

    def destroy(self):
        self.stop()
        self.container.stop()

    
    
