import socket
import redis
import uuid
import logging
import json

from .ContainerManager import ContainerManager
from .BridgeManager import BridgeManager
from .BtrfsManager import BtrfsManager
from .DiskManager import DiskManager
from .Config import Config
from .AggregatorManager import AggregatorManager
from .KvmManager import KvmManager
from .LogManager import LogManager
from .Nft import Nft
from .ZerotierManager import ZerotierManager
from .Response import Response
from .ContainerManager import BaseClient
from . import typchk


DefaultTimeout = 10  # seconds
logger = logging.getLogger('g8core')


class Client(BaseClient):
    _raw_chk = typchk.Checker({
        'id': str,
        'command': str,
        'arguments': typchk.Any(),
        'queue': typchk.Or(str, typchk.IsNone()),
        'max_time': typchk.Or(int, typchk.IsNone()),
        'stream': bool,
        'tags': typchk.Or([str], typchk.IsNone()),
    })

    def __init__(self, host, port=6379, password="", db=0, ssl=True, timeout=None, testConnectionAttempts=3):
        super().__init__(timeout=timeout)

        socket_timeout = (timeout + 5) if timeout else 15
        socket_keepalive_options = dict()
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 1
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        self._redis = redis.Redis(host=host, port=port, password=password, db=db, ssl=ssl,
                                  socket_timeout=socket_timeout,
                                  socket_keepalive=True, socket_keepalive_options=socket_keepalive_options)
        self._container_manager = ContainerManager(self)
        self._bridge_manager = BridgeManager(self)
        self._disk_manager = DiskManager(self)
        self._btrfs_manager = BtrfsManager(self)
        self._zerotier = ZerotierManager(self)
        self._kvm = KvmManager(self)
        self._logger = LogManager(self)
        self._nft = Nft(self)
        self._config = Config(self)
        self._aggregator = AggregatorManager(self)

        if testConnectionAttempts:
            for _ in range(testConnectionAttempts):
                try:
                    self.ping()
                except:
                    pass
                else:
                    return
            raise ConnectionError("Could not connect to remote host %s" % host)

    @property
    def container(self):
        """
        Container manager
        :return:
        """
        return self._container_manager

    @property
    def bridge(self):
        """
        Bridge manager
        :return:
        """
        return self._bridge_manager

    @property
    def disk(self):
        """
        Disk manager
        :return:
        """
        return self._disk_manager

    @property
    def btrfs(self):
        """
        Btrfs manager
        :return:
        """
        return self._btrfs_manager

    @property
    def zerotier(self):
        """
        Zerotier manager
        :return:
        """
        return self._zerotier

    @property
    def kvm(self):
        """
        KVM manager
        :return:
        """
        return self._kvm

    @property
    def logger(self):
        """
        Logger manager
        :return:
        """
        return self._logger

    @property
    def nft(self):
        """
        NFT manager
        :return:
        """
        return self._nft

    @property
    def config(self):
        """
        Config manager
        :return:
        """
        return self._config

    @property
    def aggregator(self):
        """
        Aggregator manager
        :return:
        """
        return self._aggregator

    def raw(self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None):
        """
        Implements the low level command call, this needs to build the command structure
        and push it on the correct queue.
        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param queue: command queue (commands on the same queue are executed sequentially)
        :param max_time: kill job server side if it exceeded this amount of seconds
        :param stream: If True, process stdout and stderr are pushed to a special queue (stream:<id>) so
            client can stream output
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Response object
        """
        if not id:
            id = str(uuid.uuid4())

        payload = {
            'id': id,
            'command': command,
            'arguments': arguments,
            'queue': queue,
            'max_time': max_time,
            'stream': stream,
            'tags': tags,
        }

        self._raw_chk.check(payload)
        flag = 'result:{}:flag'.format(id)
        self._redis.rpush('core:default', json.dumps(payload))
        if self._redis.brpoplpush(flag, flag, DefaultTimeout) is None:
            TimeoutError('failed to queue job {}'.format(id))
        logger.debug('%s >> g8core.%s(%s)', id, command, ', '.join(("%s=%s" % (k, v) for k, v in arguments.items())))

        return Response(self, id)

    def response_for(self, id):
        return Response(self, id)