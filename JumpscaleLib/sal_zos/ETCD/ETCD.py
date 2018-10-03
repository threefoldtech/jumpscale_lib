from io import BytesIO

import etcd3
import yaml

from jumpscale import j

from .. import templates
from ..abstracts import Nics, Service

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

class ETCD(Service):
    """etced server"""

    def __init__(self, node, name, data_dir='/mnt/data', zt_identity=None, nics=None, token=None, cluster=None):
        super().__init__(name, node, 'etcd', [CLIENT_PORT, PEER_PORT])
        self.flist = 'https://hub.grid.tf/tf-official-apps/etcd-3.3.4.flist'
        self.data_dir = data_dir
        self.zt_identity = zt_identity
        self._config_path = '/bin/etcd_{}.config'.format(self.name)
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
            return 'http://{}:{}'.format(self.container.mgmt_addr, CLIENT_PORT)

    @property
    def peer_url(self):
            return 'http://{}:{}'.format(self.container.mgmt_addr, PEER_PORT)

    @property
    def _container_data(self):
        """
        :return: data used for etcd container
         :rtype: dict
        """
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
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'mounts': {fs.path: self.data_dir},
            'identity': self.zt_identity,
        }

    def create_config(self):
        cluster = self.cluster if self.cluster else [{'name': self.name, 'address': self.peer_url}]
        members  = ['='.join([member['name'],member['address']]) for member in cluster]

        config = {
            'name': self.name,
            'initial_peer_urls': self.peer_url,
            'listen_peer_urls': self.peer_url,
            'listen_client_urls': self.client_url,
            'advertise_client_urls': self.client_url,
            'data_dir': self.data_dir,
            'token': self.token,
            'cluster': ','.join(members),
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
