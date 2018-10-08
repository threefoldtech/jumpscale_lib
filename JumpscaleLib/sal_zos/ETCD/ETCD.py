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

    def __init__(self, node, name, password, data_dir='/mnt/data', zt_identity=None, nics=None, token=None, cluster=None):
        super().__init__(name, node, 'etcd', [CLIENT_PORT, PEER_PORT])
        self.flist = 'https://hub.grid.tf/tf-official-apps/etcd-3.3.4.flist'
        self.data_dir = data_dir
        self.zt_identity = zt_identity
        self._config_path = '/bin/etcd_{}.config'.format(self.name)
        self.token = token
        self.cluster = cluster
        self.password = password
        self.nics = Nics(self)
        self.add_nics(nics)

    def connection_info(self):
        return {
            'ip': self.container.mgmt_addr,
            'client_port': CLIENT_PORT,
            'peer_port': PEER_PORT,
            'peer_url': self.peer_url,
            'client_url': self.client_url,
            'password': self.password
        }

    @property
    def client_url(self):
        """
        return client url 
        """

            return 'http://{}:{}'.format(self.container.mgmt_addr, CLIENT_PORT)

    @property
    def peer_url(self):
         """
        return peer url 
        """
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
    
        self.authorize_zt_nics()

        return {
            'name': self._container_name,
            'flist': self.flist,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'mounts': {fs.path: self.data_dir},
            'identity': self.zt_identity,
            'env': {'ETCDCTL_API':'3'},
        }

    def create_config(self):
        """
        create configuration of Etcd and upload it in container
        """

        self.container.upload_content(self._config_path, self._config_as_text())

    def _config_as_text(self):
        """
        render etcd config template
        """

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
        return templates.render('etcd.conf', **config).strip()

    def deploy(self, timeout=120):
        # call the container property to make sure it gets created and the ports get updated
        self.container
        if not j.tools.timer.execute_until(lambda : self.container.mgmt_addr, timeout, 1):
            raise RuntimeError('Failed to get zt ip for etcd {}'.format(self.name))


    def start(self):
        if self.is_running():
            return

        logger.info('start etcd {}'.format(self.name))

        self.create_config()
        cmd = '/bin/etcd --config-file {}'.format(self._config_path)
        self.container.client.system(cmd, id=self._id)
        if not j.tools.timer.execute_until(self.is_running, 30, 0.5):
            raise RuntimeError('Failed to start etcd server: {}'.format(self.name))
        self._enable_auth()

    def _enable_auth(self):
        """
        enable authentication of etcd user 
        """

        commands = [
            '/bin/etcdctl --endpoints={} user add root:{}'.format(self.client_url, self.password),
            '/bin/etcdctl --endpoints={} auth enable'.format(self.client_url),
        ]

        for command in commands:
            result = self.container.client.system(command).get()
            if result.state == 'ERROR':
                if result.stderr == 'Error: etcdserver: user name not found\n':
                    # this command has been executed before
                    continue
                else:
                    raise RuntimeError(result.stderr)
