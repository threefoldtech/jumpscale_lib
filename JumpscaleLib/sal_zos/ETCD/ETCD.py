from io import BytesIO

import etcd3
import yaml

from jumpscale import j

from .. import templates
from ..abstracts import Nics

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

    def __init__(self, node, name, listen_peer_urls=None, listen_client_urls=None, initial_advertise_peer_urls=None, advertise_client_urls=None, data_dir='/mnt/data', zt_identity=None, nics=None, token=None, cluster=None):
        self.node = node
        self.name = name
        self._container = None
        self.flist = 'https://hub.grid.tf/bola_nasr_1/etcd-3.3.4.flist'
        self.listen_peer_urls = listen_peer_urls
        self.listen_client_urls = listen_client_urls
        self.initial_advertise_peer_urls = initial_advertise_peer_urls
        self.advertise_client_urls = advertise_client_urls
        self.data_dir = data_dir
        self.zt_identity = zt_identity
        self._id = 'etcd.{}'.format(self.name)
        self._config_path = '/bin/etcd_{}.config'.format(self.name)
        self._container_name = 'etcd_{}'.format(self.name)
        self._mount_point = '/mnt/etcds/{}'.format(self.name)
        self.token = token
        self.cluster = cluster
        self.nics = Nics(self)
        if nics:
            for nic in nics:
                nicobj = self.nics.add(nic['name'], nic['type'], nic['id'], nic.get('hwaddr'))
                if nicobj.type == 'zerotier':
                    nicobj.client_name = nic.get('ztClient')
        if 'nat0' not in self.nics:
            self.nics.add('nat0', 'default')

    @property
    def client_url(self):
            return 'http://{}:{}'.format(self.container.public_addr, CLIENT_PORT)

    @property
    def peer_url(self):
            return 'http://{}:{}'.format(self.container.public_addr, PEER_PORT)

    def _container_data(self):
        """
        :return: data used for etcd container
         :rtype: dict
        """
        ports = self.node.freeports(2)
        if len(ports) <= 0:
            raise RuntimeError("can't install etcd, no free port available on the node")

        ports = {
            str(ports[0]): CLIENT_PORT,
            str(ports[1]): PEER_PORT,
        }

        sp = self.node.find_persistance()
        try:
            fs = sp.get(self._container_name)
        except ValueError:
            fs = sp.create(self._container_name)
    
        if not self.zt_identity:
            self.zt_identity = self.node.client.system('zerotier-idtool generate').get().stdout.strip()
        zt_public = self.node.client.system('zerotier-idtool getpublic {}'.format(self.zt_identity)).get().stdout.strip()
        j.sal_zos.utils.authorize_zerotiers(zt_public, self.nics)

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'mounts': {fs.path: self.data_dir},
            'identity': self.zt_identity,
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
                self._container = self.node.containers.get(self._container_name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data())
        return self._container
    

    def create_config(self):
        client = 'http://{}:{}'.format(self.container.public_addr, CLIENT_PORT)
        peer = 'http://{}:{}'.format(self.container.public_addr, PEER_PORT)

        peer_urls = ','.join(self.listen_peer_urls) if self.listen_peer_urls else peer
        initial_peer_urls = ','.join(self.initial_advertise_peer_urls) if self.initial_advertise_peer_urls else peer
        client_urls = ','.join(self.listen_client_urls) if self.listen_client_urls else client
        advertise_client_urls = ','.join(self.advertise_client_urls) if self.advertise_client_urls else client

        cluster = self.cluster if self.cluster else [{'name': self.name, 'address': peer}]
        members  = ['='.join([member['name'],member['address']]) for member in cluster]


        config = {
            "name": self.name,
            "initial_peer_urls": initial_peer_urls,
            "listen_peer_urls": peer_urls,
            "listen_client_urls": client_urls,
            "advertise_client_urls": advertise_client_urls,
            "data_dir": self.data_dir,
            "token": self.token,
            "cluster": ",".join(members),
        }
        templates.render('etcd.conf', **config).strip()
        self.container.upload_content(self._config_path, templates.render('etcd.conf', **config).strip())

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


    def start(self):
        if self.is_running():
            return

        logger.info('start etcd {}'.format(self.name))

        self.create_config()
        cmd = '/bin/etcd --config-file {}'.format(self._config_path)
        self.container.client.system(cmd, id=self._id)
        if not j.tools.timer.execute_until(self.is_running, 30, 0.5):
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
        if not self._container_exists():
            return False
        try:
            self.container.client.job.list(self._id)
        except:
            return False
        for port in [PEER_PORT, CLIENT_PORT]:
            if not self.container.is_port_listening(port):
                return False
        return True

    def put(self, key, value):
        client = j.clients.etcd.get(self.name, data={'host': self.container.public_addr, 'port': CLIENT_PORT})

        if value.startswith("-"):
            value = "-- %s" % value
        if key.startswith("-"):
            key = "-- %s" % key
        client.api.put(key, value)

    def destroy(self):
        if not self._container_exists():
            return

        self.stop()
        self.container.stop()

    def _container_exists(self):
        try:
            self.node.containers.get(self._container_name)
            return True
        except LookupError:
            return False
