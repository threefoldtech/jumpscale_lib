import signal
import time

from Jumpscale import j

from .. import templates
from ..abstracts import Service

logger = j.logger.get(__name__)
DEFAULT_PORT = 9000


class Minio(Service):
    """
    Minio gateway
    """

    def __init__(self,
                 name,
                 node,
                 login,
                 password,
                 zdbs,
                 namespace,
                 private_key,
                 namespace_secret='',
                 block_size=1048576,
                 meta_private_key='',
                 nr_datashards=1,
                 nr_parityshards=0,
                 tlog_namespace=None,
                 tlog_address=None,
                 master_namespace=None,
                 master_address=None):
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
        :param tlog_namespace: name of the zerodb namespace used as tlog
        :param tlog_address: ip:port of the zerodb namespace used as tlog
        :param master_namespace: name of the zerodb namespace used as master
        :param master_address: ip:port of the zerodb namespace used as master
        """
        super().__init__(name, node, 'minio', [DEFAULT_PORT])

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
        self.tlog = None
        self.master = None
        if tlog_namespace and tlog_address:
            self.tlog = {
                'namespace': tlog_namespace,
                'address': tlog_address,
                'password': namespace_secret}
        if master_namespace and master_address:
            self.master = {
                'namespace': master_namespace,
                'address': master_address,
                'password': namespace_secret}

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
            fs = sp.get(self._id)
        except ValueError:
            fs = sp.create(self._id)

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': {ports[0]: DEFAULT_PORT},
            'nics': [{'type': 'default'}],
            'env': envs,
            'mounts': {fs.path: metadata_path},
        }

    def start(self, timeout=15):
        """
        Start minio gatway
        :param timeout: time in seconds to wait for the minio gateway to start
        """
        if self.is_running():
            return

        logger.info('start minio %s' % self.name)

        self.create_config()

        cmd = '/bin/minio gateway zerostor --address 0.0.0.0:{port} --config-dir {dir}'.format(
            port=DEFAULT_PORT, dir=self._config_dir)

        # wait for minio to start
        self.container.client.system(cmd, id=self._id)
        if not j.tools.timer.execute_until(self.is_running, 30, 0.5):
            raise RuntimeError('Failed to start minio server: {}'.format(self.name))

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
            zdbs=self.zdbs, private_key=self.private_key, block_size=self.block_size, nr_datashards=self._nr_datashards,
            nr_parityshards=self._nr_parityshards, tlog=self.tlog, master=self.master).strip()

    @property
    def node_port(self):
        return self.container.get_forwarded_port(DEFAULT_PORT)

    def reload(self):
        """
        tell minio process to reload its configuration by reading the config file again
        """
        if not self.is_running():
            logger.error("cannot reload when minio is not running")
            return

        self.container.client.job.kill(self._id, signal.SIGHUP)

    def destroy(self):
        super().destroy()

        sp = self.node.storagepools.get('zos-cache')
        try:
            fs = sp.get(self._id)
            fs.delete()
        except ValueError:
            pass
