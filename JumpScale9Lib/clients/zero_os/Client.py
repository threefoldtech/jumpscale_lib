import redis
import uuid
import json
import textwrap
import shlex
import base64
import signal
import socket
import logging
import time
import sys
from js9 import j
from .AggregatorManager import AggregatorManager
from .BridgeManager import BridgeManager
from .BtrfsManager import BtrfsManager
from .InfoManager import InfoManager
from .Config import Config
from .ContainerManager import *
from .DiskManager import *
from .FilesystemManager import *
from .IPManager import *
from .JobManager import *
from .KvmManager import *
from .LogManager import *
from .Nft import *
from .ProcessManager import *
from .ZerotierManager import *

DefaultTimeout = 10  # seconds

class JobNotFoundError(Exception):
    pass


class ResultError(RuntimeError):
    def __init__(self, msg, code=0):
        super().__init__(msg)
        self._message = msg
        self._code = code

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


class Return:

    def __init__(self, payload):
        self._payload = payload

    @property
    def payload(self):
        """
        Raw return object data
        :return: dict
        """
        return self._payload

    @property
    def id(self):
        """
        Job ID
        :return: string
        """
        return self._payload['id']

    @property
    def data(self):
        """
        Data returned by the process. Only available if process
        output data with the correct core level

        For example, if a job returns a json object the self.level will be 20 and the data will contain the serialized
        json object, other levels exists for yaml, toml, etc... it really depends on the running job
        return: python primitive (str, number, dict or array)
        """
        return self._payload['data']

    @property
    def level(self):
        """
        Data message level (if any)
        """
        return self._payload['level']

    @property
    def starttime(self):
        """
        Starttime as a timestamp
        """
        return self._payload['starttime'] / 1000

    @property
    def time(self):
        """
        Execution time in millisecond
        """
        return self._payload['time']

    @property
    def state(self):
        """
        Exit state
        :return: str one of [SUCCESS, ERROR, KILLED, TIMEOUT, UNKNOWN_CMD, DUPLICATE_ID]
        """
        return self._payload['state']

    @property
    def stdout(self):
        """
        The job stdout
        :return: string or None
        """
        streams = self._payload.get('streams', None)
        return streams[0] if streams is not None and len(streams) >= 1 else ''

    @property
    def stderr(self):
        """
        The job stderr
        :return: string or None
        """
        streams = self._payload.get('streams', None)
        return streams[1] if streams is not None and len(streams) >= 2 else ''

    @property
    def code(self):
        """
        Exit code of the job, this can be either one of the http codes, of (if the value > 1000)
        is the exit code of the underlaying process
        if code > 1000:
            exit_code = code - 1000

        """
        return self._payload.get('code', 500)

    def __repr__(self):
        return str(self)

    def __str__(self):
        tmpl = """\
        STATE: {code} {state}
        STDOUT:
        {stdout}
        STDERR:
        {stderr}
        DATA:
        {data}
        """

        return textwrap.dedent(tmpl).format(code=self.code, state=self.state, stdout=self.stdout, stderr=self.stderr, data=self.data)


class Response:
    def __init__(self, client, id):
        self._client = client
        self._id = id
        self._queue = 'result:{}'.format(id)

    @property
    def id(self):
        """
        Job ID
        :return: string
        """
        return self._id

    @property
    def exists(self):
        """
        Returns true if the job is still running or zero-os still knows about this job ID

        After a job is finished, a job remains on zero-os for max of 5min where you still can read the job result
        after the 5 min is gone, the job result is no more fetchable
        :return: bool
        """
        r = self._client._redis
        flag = '{}:flag'.format(self._queue)
        return bool(r.execute_command('LKEYEXISTS', flag))

    @property
    def running(self):
        """
        Returns true if job still in running state
        :return:
        """
        r = self._client._redis
        flag = '{}:flag'.format(self._queue)
        if bool(r.execute_command('LKEYEXISTS', flag)):
            return r.execute_command('LTTL', flag) == -1

        return False

    def stream(self, callback=None):
        """
        Runtime copy of job messages. This required the 'stream` flag to be set to True otherwise it will
        not be able to copy any output, while it will block until the process exits.

        :note: This function will block until it reaches end of stream or the process is no longer running.

        :param callback: callback method that will get called for each received message
                         callback accepts 3 arguments
                         - level int: the log message levels, refer to the docs for available levels
                                      and their meanings
                         - message str: the actual output message
                         - flags int: flags associated with this message
                                      - 0x2 means EOF with success exit status
                                      - 0x4 means EOF with error

                                      for example (eof = flag & 0x6) eof will be true for last message u will ever
                                      receive on this callback.

                         Note: if callback is none, a default callback will be used that prints output on stdout/stderr
                         based on level.
        :return: None
        """
        if callback is None:
            callback = Response.__default

        if not callable(callback):
            raise Exception('callback must be callable')

        queue = 'stream:%s' % self.id
        r = self._client._redis

        # we can terminate quickly by checking if the process is not running and it has no queued output.
        if not self.running and r.llen(queue) == 0:
            return

        while True:
            data = r.blpop(queue, 10)
            if data is None:
                if not self.running:
                    break
                continue
            _, body = data
            payload = json.loads(body.decode())
            message = payload['message']
            line = message['message']
            meta = message['meta']
            callback(meta >> 16, line, meta & 0xff)

            if meta & 0x6 != 0:
                break

    @staticmethod
    def __default(level, line, meta):
        w = sys.stdout if level == 1 else sys.stderr
        w.write(line)
        w.write('\n')

    def get(self, timeout=None):
        """
        Waits for a job to finish (max of given timeout seconds) and return job results. When a job exits get() will
        keep returning the same result until zero-os doesn't remember the job anymore (self.exists == False)

        :notes: the timeout here is a client side timeout, it's different than the timeout given to the job on start
        (like in system method) witch will cause the job to be killed if it exceeded this timeout.

        :param timeout: max time to wait for the job to finish in seconds
        :return: Return object
        """
        if timeout is None:
            timeout = self._client.timeout
        r = self._client._redis
        start = time.time()
        maxwait = timeout
        while maxwait > 0:
            if not self.exists:
                raise JobNotFoundError(self.id)
            v = r.brpoplpush(self._queue, self._queue, min(maxwait, 10))
            if v is not None:
                payload = json.loads(v.decode())
                r = Return(payload)
                logger.debug('%s << %s, stdout="%s", stderr="%s", data="%s"',
                             self._id, r.state, r.stdout, r.stderr, r.data[:1000])
                return r
            logger.debug('%s still waiting (%ss)', self._id, int(time.time() - start))
            maxwait -= 10
        raise TimeoutError()


class JSONResponse(Response):
    def __init__(self, response):
        super().__init__(response._client, response.id)

    def get(self, timeout=None):
        """
        Get response as json, will fail if the job doesn't return a valid json response

        :param timeout: client side timeout in seconds
        :return: int
        """
        result = super().get(timeout)
        if result.state != 'SUCCESS':
            raise ResultError(result.data, result.code)
        if result.level != 20:
            raise ResultError('not a json response: %d' % result.level, 406)

        return json.loads(result.data)


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