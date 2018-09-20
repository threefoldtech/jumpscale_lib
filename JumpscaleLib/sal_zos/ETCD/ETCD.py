from io import BytesIO

import etcd3
import yaml
from .. import templates


logger = j.logger.get(__name__)

CLIENT_PORT = 2379
PEER_PORT = 2380


class EtcdCluster():
    """etced server"""

    def __init__(self, name, dialstrings, mgmtdialstrings, logger=None):

        self.name = name
        self.dialstrings = dialstrings
        self.mgmtdialstrings = mgmtdialstrings
        self._ays = None
        self._client = None

    def _connect(self):
        dialstrings = self.mgmtdialstrings.split(",")
        for dialstring in dialstrings:
            host, port = dialstring.split(":")
            try:
                self._client = etcd3.client(host=host, port=port, timeout=5)
                self._client.status()
                return  # connection is valid
            except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError) as err:
                self._client = None
                self.logger.error("Could not connect to etcd on %s:%s : %s" % (host, port, str(err)))

        if self._client is None:
            raise RuntimeError("can't connect to etcd on %s" % self.mgmtdialstrings)

    # TODO: replace code duplication with decorator ?

    def put(self, key, value):
        if not self._client:
            self._connect()
        try:
            self._client.put(key, value)
        except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError):
            self._connect()
            self.put(key, value)

    def delete(self, key):
        if not self._client:
            self._connect()
        try:
            self._client.delete(key)
        except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError):
            self._connect()
            self.delete(key)

class ETCD():
    """etced server"""

    def __init__(self, node, name, listen_peer_urls=None, listen_client_urls=None, initial_advertise_peer_urls=None, advertise_client_urls=None, data_dir='/mnt/data', client_port=CLIENT_PORT, peer_port=PEER_PORT):
        self.node = node
        self.name = name
        self._container = None
        self.flist = 'https://hub.grid.tf/bola_nasr_1/etcd-3.3.4.flist'
        self.listen_peer_urls = listen_peer_urls
        self.listen_client_urls = listen_client_urls
        self.initial_advertise_peer_urls = initial_advertise_peer_urls
        self.advertise_client_urls = advertise_client_urls
        self.data_dir = data_dir
        self.client_port = client_port
        self.peer_port = peer_port
        self._id = 'etcd.{}'.format(self.name)
        self._config_path = '/bin/etcd_{}.config'.format(self.name)

    @property
    def _container_data(self):
        """
        :return: data used for etcd container
         :rtype: dict
        """
        ports = self.node.freeports(2)
        if len(ports) <= 0:
            raise RuntimeError("can't install etcd, no free port available on the node")

        self.client_port = ports[0]
        self.peer_port = ports[1]
        ports = {
            self.client_port: CLIENT_PORT,
            self.peer_port: PEER_PORT
        }

        return {
            'name': self.name,
            'flist': self.flist,
            'ports': ports,
            'nics': [{'type': 'default'}],
        }

    @property
    def container(self):
        """
        Get/create etcd container to run etcd services on
        :return: etcd container
        :rtype: container sal object
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self.name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data)
        return self._container
    

    def create_config(self):
        client = 'http://{}:{}'.format(self.node.public_addr, self.client_port)
        peer = 'http://{}:{}'.format(self.node.public_addr, self.peer_port)

        peer_urls = ','.join(self.listen_peer_urls) if self.listen_peer_urls else peer
        initial_peer_urls = ','.join(self.initial_advertise_peer_urls) if self.initial_advertise_peer_urls else peer
        client_urls = ','.join(self.listen_client_urls) if self.listen_client_urls else client
        advertise_client_urls = ','.join(self.advertise_client_urls) if self.advertise_client_urls else client


        config = {
            "name": self.name,
            "initial-advertise-peer-urls": initial_peer_urls,
            "listen_peer_urls": peer_urls,
            "listen_client_urls": client_urls,
            "advertise_client_urls": advertise_client_urls,
            "data_dir": self.data_dir,
        }
        templates.render('etcd.conf', **config).strip()
        self.container.upload_content(self._config_path, templates.render('etcd.conf', **config).strip())

    def deploy(self):
        # call the container property to make sure it gets created and the ports get updated
        self.container

    def start(self):
        if self.is_running():
            return

        logger.info('start etcd {}'.format(self.name))

        self.create_config()
        cmd = '/bin/etcd --config-file {}'.format(self._config_path)
        self.container.client.system(cmd, id=self._id)
        if not self.container.is_port_listening(PEER_PORT):
            raise RuntimeError('Failed to start etcd server: {}'.format(self.name))

    def stop(self):
        import time

        if not self.is_running():
            return

        self.container.client.job.kill(self._id)
        start = time.time()
        while start + 15 > time.time():
            time.sleep(1)
            try:
                self.container.client.job.list(self._id)
            except RuntimeError:
                return
            continue

        raise RuntimeError('failed to stop etcd.')

    def is_running(self):
        try:
            for _ in self.container.client.job.list(self._id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def put(self, key, value):
        client = 'http://{}:{}'.format(self.node.public_addr, self.client_port)
        client_urls = ','.join(self.listen_client_urls) if self.listen_client_urls else client

        if value.startswith("-"):
            value = "-- %s" % value
        if key.startswith("-"):
            key = "-- %s" % key
        cmd = '/bin/etcdctl \
          --endpoints {etcd} \
          put {key} "{value}"'.format(etcd=client_urls, key=key, value=value)
        return self.container.client.system(cmd, env={"ETCDCTL_API": "3"}).get()

    def destroy(self):
        self.stop()
        self.container.stop()
