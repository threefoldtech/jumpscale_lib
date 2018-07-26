import redis
import time

from js9 import j

from ..abstracts import Nics
from ..utils import authorize_zerotiers
from ..Disk import Disk
from .namespace import Namespaces

logger = j.logger.get(__name__)
DEFAULT_PORT = 9900


class Zerodb:
    def __init__(self, node, name, path=None, mode='user', sync=False, admin='', node_port=DEFAULT_PORT):
        """
        Create zerodb object

        To deploy zerodb invoke .deploy method

        :param node: the node on which the zerodb is created
        :type: node: node sal object
        :param name: Name of the zerodb
        :type name: str
        :param pat: path zerodb stores data on
        :type path: str
        :param mode: zerodb running mode
        :type mode: str
        :param sync: zerodb sync
        :type sync: bool
        :param admin: zerodb admin password
        :type admin: str
        :param node_port: the port the zerodb container will forward to. If this port is not free, the deploy will find the next free port.
        :type: int
        """
        self.name = name
        self.node = node
        self.zt_identity = None
        self._container = None
        self.flist = 'https://hub.gig.tech/gig-autobuilder/rivine-0-db-release-master.flist'

        self._mode = mode
        self._sync = sync
        self._admin = admin
        self._node_port = node_port
        self._path = None

        # call setters to enforce validation
        self.mode = mode
        self.admin = admin
        self.sync = sync
        self.node_port = node_port

        if path:
            self.path = path

        self.namespaces = Namespaces(self)
        self.nics = Nics(self)
        self.nics.add('nat0', 'default')
        self.__redis = None
        self._id = 'zerodb.{}'.format(self.name)

    @property
    def _redis(self):
        """
        Get redis connection

        :return: redis client used to execute commands on zerodb
        :rtype: Redis class
        """
        if self.__redis is None:
            ip = self.container.node.addr
            port = DEFAULT_PORT
            password = self.admin

            if ip == '127.0.0.1':
                ip = self.container.default_ip().ip.format()
            else:
                # use the connection below if you want to test a dev setup and to execute it from outside the node
                port = self.node_port

            self.__redis = redis.Redis(host=ip, port=port, password=password)
            self.__redis.ping()

        return self.__redis

    @property
    def info(self):
        info = self.node.client.btrfs.info(self.node.get_mount_path(self.path))
        used = 0
        total = 0
        reserved = 0
        devicename = None
        for device in info['devices']:
            used += device['used']
            total += device['size']
            devicename = device['path']

        device = self.node.disks.get_device(devicename)
        devicetype = None
        if isinstance(device, Disk):
            devicetype = device.type.value
        else:
            devicetype = device.disk.type.value
        for namespace in self.namespaces:
            reserved += namespace.size * 1024 ** 3

        return {
            'used': used,
            'reserved': reserved,
            'total': total,
            'free': total - reserved,
            'path': self.path,
            'mode': self.mode,
            'sync': self.sync,
            'type': devicetype
        }

    @property
    def _container_data(self):
        """
        :return: data used for zerodb container
         :rtype: dict
        """
        ports = self.node.freeports(self.node_port, 1)
        if len(ports) <= 0:
            raise RuntimeError("can't install 0-db, no free port available on the node")

        self.node_port = ports[0]
        if not self.zt_identity:
            self.zt_identity = self.node.client.system('zerotier-idtool generate').get().stdout.strip()
        zt_public = self.node.client.system('zerotier-idtool getpublic {}'.format(self.zt_identity)).get().stdout.strip()
        authorize_zerotiers(zt_public, self.nics)

        return {
            'name': self._container_name,
            'flist': self.flist,
            'identity': self.zt_identity,
            'mounts': {self.path: '/zerodb'},
            'ports': {"zt*:%s" % self.node_port: DEFAULT_PORT},
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics]
        }

    @property
    def _container_name(self):
        """
        :return: name used for zerodb container
        :rtype: string
        """
        return 'zdb_{}'.format(self.name)

    @property
    def container(self):
        """
        Get/create zerodb container to run zerodb services on
        :return: zerodb container
        :rtype: container sal object
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self._container_name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data)
        return self._container

    def load_from_reality(self, container=None):
        """
        loads zerodb data from reality.
        Loads node_port, path, sync, mode and admin

        :param container: zerodb container
        :type container: container sal object
        """
        if not container:
            container = self.node.containers.get(self._container_name)
        for k, v in container.ports.items():
            if v == DEFAULT_PORT:
                self.node_port = int(k)
                break
        for k, v in container.mounts.items():
            if v == '/zerodb':
                self.path = k

        running, args = self.is_running()
        if running:
            for arg in args:
                if arg == '--sync':
                    self.sync = True
                if arg == '--mode':
                    self.mode = args[args.index(arg) + 1]
                if arg == '--admin':
                    self.admin = args[args.index(arg) + 1]

    def from_dict(self, data):
        """
        Update zerodb from data.
        Updates mode, admin, sync, path, node_port, and namespaces.

        :param data: zerodb data
        :type data: dict
        """
        self.nics = Nics(self)
        self.mode = data.get('mode', 'user')
        self.admin = data.get('admin', '')
        self.zt_identity = data.get('ztIdentity')
        self.sync = data.get('sync', False)
        self.path = data['path']
        self.node_port = data.get('nodePort', DEFAULT_PORT)
        for namespace in data.get('namespaces', []):
            self.namespaces.add(
                namespace['name'], namespace.get('size'), namespace.get('password'), namespace.get('public', True))
        for nic in data.get('nics', []):
            nicobj = self.nics.add(nic['name'], nic['type'], nic['id'], nic.get('hwaddr'))
            if nicobj.type == 'zerotier':
                nicobj.client_name = nic.get('ztClient')
        if 'nat0' not in self.nics:
            self.nics.add('nat0', 'default')

    def to_dict(self):
        """
        Convert zerodb object to dict
        :return: dict containing zerodb data
        :rtype: dict
        """
        namespaces = []
        for namespace in self.namespaces:
            namespaces.append({
                'name': namespace.name,
                'size': namespace.size if namespace.size else 0,
                'password': namespace.password,
                'public': namespace.public,
            })

        return {
            'mode': self.mode,
            'sync': self.sync,
            'nodePort': self.node_port,
            'admin': self.admin,
            'ztIdentity': self.zt_identity,
            'path': self.path,
            'nics': [nic.to_dict() for nic in self.nics],
            'namespaces': namespaces,
        }

    def to_json(self):
        """
        json serialize zerodb dict

        :return: a json formatted string of self.to_dict
        :rtype: str
        """
        return j.data.serializer.json.dumps(self.to_dict())

    def deploy(self):
        """
        Deploy zerodb by creating a container and running zerodb in the container, creating the namespaces in self.namespaces and
        removing namespaces that are not in self.namespaces.
        """
        if not self.container.is_running():
            self.container.start()

        for i in range(5):
            try:
                self.container.client.ping()
                break
            except RuntimeError as err:
                if str(err).find('failed to dispatch command to container'):
                    time.sleep(1)

        self.start()

        live_namespaces = self._live_namespaces()

        for namespace in self.namespaces:
            namespace.deploy(live_namespaces)

        for namespace in live_namespaces:
            if namespace not in self.namespaces and namespace != 'default':
                self._redis.execute_command('NSDEL', namespace)

    def is_running(self):
        """
        Check if zerodb process is running
        :return: True if running, False if halted. And the the job arguments.
        :rtype: a type. of the status and arguments list ex: (True, ['--mode', 'seq'])
        """
        try:
            for job in self.container.client.job.list(self._id):
                runstatus = self.container.is_port_listening(DEFAULT_PORT, None)
                return runstatus, job['cmd']['arguments']['args']
            return False, []
        except Exception as err:
            if str(err).find("invalid container id"):
                return False, []
            raise

    def start(self, timeout=15):
        """
        Start zero db server
        :param timeout: time in seconds to wait for the zerodb server to start
        :type timeout: int
        """
        is_running, _ = self.is_running()
        if is_running:
            return

        logger.info('start zerodb %s' % self.name)

        cmd = '/bin/zdb \
            --port {port} \
            --data /zerodb/data \
            --index /zerodb/index \
            --mode {mode} \
            '.format(port=DEFAULT_PORT, mode=self.mode)
        if self.sync:
            cmd += ' --sync'
        if self.admin:
            cmd += ' --admin {}'.format(self.admin)

        # wait for zerodb to start
        self.container.client.system(cmd, id=self._id)
        is_running = self.container.is_port_listening(DEFAULT_PORT, timeout)

        if not is_running:
            raise RuntimeError('Failed to start zerodb server: {}'.format(self.name))

    def stop(self, timeout=30):
        """
        Stop the zerodb server
        :param timeout: time in seconds to wait for the zerodb server to stop
        :type timeout: int
        """
        if not self.container.is_running():
            return

        is_running, _ = self.is_running()
        if not is_running:
            self.container.stop()
            return

        logger.info('stop zerodb %s' % self.name)

        self.container.client.job.kill(self._id)

        # wait for zerodb to stop
        start = time.time()
        end = start + timeout
        is_running, _ = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running, _ = self.is_running()

        if is_running:
            raise RuntimeError('Failed to stop zerodb server: {}'.format(self.name))

        self.container.stop()

    def _live_namespaces(self):
        """
        List the namespaces created on zerodb.

        :return: a list of namespaces
        :rtype: list of strings
        """
        result = self._redis.execute_command('NSLIST')
        return [namespace.decode('utf-8') for namespace in result]

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if not value:
            raise ValueError('path can\'t be empty')
        if type(value) != str:
            raise ValueError('path must be a string')
        self._path = value

    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, value):
        self._admin = value

    @property
    def sync(self):
        return self._sync

    @sync.setter
    def sync(self, value):
        if type(value) != bool:
            raise ValueError('sync must be a boolen')
        self._sync = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ['user', 'seq', 'direct']:
            raise ValueError('mode must be user, seq or direct')
        self._mode = value

    @property
    def node_port(self):
        return self._node_port

    @node_port.setter
    def node_port(self, value):
        if type(value) != int:
            raise ValueError('node port must be type int')
        self._node_port = value

    def __str__(self):
        return "Zerodb {}".format(self.name)

    def __repr__(self):
        return str(self)
