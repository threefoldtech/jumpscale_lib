import time
from Jumpscale import j
from .. import templates


logger = j.logger.get(__name__)
DEFAULT_PORT = 9000


class Minio:
    """
    Minio gateway
    """

    def __init__(self, name, node, login, password, zdbs, namespace, private_key, namespace_secret='', block_size=1048576, meta_private_key='', nr_datashards=1, nr_parityshards=0):
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
        :param nr_datashards: number of datashards.
        :param nr_parityshards: number of parityshards (if it's zero it will make the mode replication otherwise mode is distribution)
        """
        self.name = name
        self.id = 'minio.{}'.format(self.name)
        self.node = node
        self._container = None
        # self.flist = 'https://hub.grid.tf/tf-official-apps/minio.flist'
        self.flist = 'https://hub.grid.tf/tf-autobuilder/threefoldtech-minio-zerostor.flist'  # TODO replace me when merging to master
        self.zdbs = zdbs
        self._nr_datashards = nr_datashards
        self._nr_parityshards = nr_parityshards
        self.namespace = namespace
        self.private_key = private_key
        self.namespace_secret = namespace_secret
        self.block_size = block_size
        self.login = login
        self.password = password
        self.meta_private_key = meta_private_key

        self._config_dir = '/bin'
        self._config_name = 'zerostor.yaml'

    @property
    def _container_data(self):
        """
        :return: data used for zerodb container
         :rtype: dict
        """
        ports = self.node.freeports(1)
        if len(ports) <= 0:
            raise RuntimeError("can't install minio, no free port available on the node")

        metadata_path = '/minio_metadata'
        envs = {
            'MINIO_ACCESS_KEY': self.login,
            'MINIO_SECRET_KEY': self.password,
            'MINIO_ZEROSTOR_META_PRIVKEY': self.meta_private_key,
            'MINIO_ZEROSTOR_META_DIR': metadata_path,
        }

        sp = self.node.storagepools.get('zos-cache')
        try:
            fs = sp.get(self.id)
        except ValueError:
            fs = sp.create(self.id)

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': {ports[0]: DEFAULT_PORT},
            'nics': [{'type': 'default'}],
            'env': envs,
            'mounts': {fs.path: metadata_path},
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

        self.create_config()

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

    def is_running(self):
        try:
            for _ in self.container.client.job.list(self.id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    @property
    def mode(self):
        return "replication" if self._nr_parityshards <= 0 else "distribution"

    def create_config(self):
        logger.info('Creating minio config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):
        return templates.render(
            'minio.conf', namespace=self.namespace, namespace_secret=self.namespace_secret,
            zdbs=self.zdbs, private_key=self.private_key, block_size=self.block_size, nr_datashards=self._nr_datashards, nr_parityshards=self._nr_parityshards).strip()

    @property
    def node_port(self):
        try:
            container = self.node.containers.get(self._container_name)
            for k, v in container.ports.items():
                if v == DEFAULT_PORT:
                    return int(k.split(':')[-1])
        except LookupError:
            return None

    def destroy(self):
        self.stop()
        self.container.stop()
        sp = self.node.storagepools.get('zos-cache')
        try:
            fs = sp.get(self.id)
            fs.delete()
        except ValueError:
            pass
