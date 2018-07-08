import redis
import time

from js9 import j

from . import templates


logger = j.logger.get(__name__)
DEFAULT_PORT = 9000


class Minio:
    """
    Minio gateway
    """

    def __init__(self, name, node, login, password, zdbs, namespace, private_key, namespace_secret='', node_port=DEFAULT_PORT, block_size=1048576, restic_username='', restic_password='', meta_private_key=''):
        """

        :param name: instance name
        :param node: sal of the node to deploy minio on
        :param login: minio access key
        :param password minio secret key
        :param zdbs: a list of zerodbs addresses ex: ['0.0.0.0:9100']
        :param namespace: name of the zerodb namespace
        :param private_key: encryption private key
        :param namespace_secret: secret of the zerodb namespace
        :param node_port: the port the minio container will forward to. If this port is not free, the deploy will find the next free port
        """
        self.name = name
        self.id = 'minio.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.gig.tech/gig-official-apps/minio.flist'
        self.node_port = node_port
        self.zdbs = zdbs
        self.namespace = namespace
        self.private_key = private_key
        self.namespace_secret = namespace_secret
        self.block_size = block_size
        self.login = login
        self.password = password
        self.restic_username = restic_username
        self.restic_password = restic_password
        self.meta_private_key = meta_private_key

        self._config_dir = '/bin'
        self._config_name = 'zerostor.yaml'

    @property
    def _container_data(self):
        """
        :return: data used for zerodb container
         :rtype: dict
        """
        ports = self.node.freeports(self.node_port, 1)
        if len(ports) <= 0:
            raise RuntimeError("can't install minio, no free port available on the node")

        self.node_port = ports[0]

        envs = {
                'MINIO_ACCESS_KEY': self.login,
                'MINIO_SECRET_KEY': self.password,
                'AWS_ACCESS_KEY_ID': self.restic_username,
                'AWS_SECRET_ACCESS_KEY': self.restic_password,
                'MINIO_ZEROSTOR_META_PRIVKEY': self.meta_private_key,
        }

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': {self.node_port: DEFAULT_PORT},
            'nics': [{'type': 'default'}],
            'env': envs,
        }

    @property
    def _container_name(self):
        """
        :return: name used for zerodb container
        :rtype: string
        """
        return 'minio_{}'.format(self.name)

    @property
    def container(self):
        """
        Get/create minio container to run minio services on
        :return: minio container
        :rtype: container sal object
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self._container_name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data)
        return self._container

    def stop(self, timeout=30):
        """
        Stop the minio gateway
        :param timeout: time in seconds to wait for the minio gateway to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.info('stop minio %s' % self.name)

        self.container.client.job.kill(self.id)

        # wait for minio to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if is_running:
            raise RuntimeError('Failed to stop minio server: {}'.format(self.name))

        self.container.node.client.nft.drop_port(self.node_port)
        self.container.stop()

    def start(self, timeout=15):
        """
        Start minio gatway
        :param timeout: time in seconds to wait for the minio gateway to start
        """
        is_running = self.is_running()
        if is_running:
            return

        logger.info('start minio %s' % self.name)

        cmd = '/bin/minio gateway zerostor --address 0.0.0.0:{port} --config-dir {dir}'.format(
            port=DEFAULT_PORT, dir=self._config_dir)

        # wait for minio to start
        self.container.client.system(cmd, id=self.id)
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if not is_running:
            raise RuntimeError('Failed to start minio server: {}'.format(self.name))

        self.container.node.client.nft.open_port(self.node_port)

    def is_running(self):
        try:
            for _ in self.container.client.job.list(self.id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def create_config(self):
        logger.info('Creating minio config for %s' % self.name)
        config = templates.render(
            'minio.conf', namespace=self.namespace, namespace_secret=self.namespace_secret,
            zdbs=self.zdbs, private_key=self.private_key, block_size=self.block_size, nr_shards=len(self.zdbs)).strip()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def destroy(self):
        self.stop()
        self.container.stop()
