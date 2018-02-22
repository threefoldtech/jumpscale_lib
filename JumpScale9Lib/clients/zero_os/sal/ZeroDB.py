import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZeroDB:
    """
    ZeroDB server
    """

    def __init__(self, name, container, addr='0.0.0.0', port=9900, data_dir='/mnt/data',
                 index_dir='/mnt/index', mode='user', sync=False):
        self.name = name
        self.container = container
        self.addr = addr
        self.port = port
        self.data_dir = data_dir
        self.index_dir = index_dir
        self.mode = mode
        self.sync = sync
        self._ays = None

    def stop(self, timeout=30):
        """
        Stop the zerodb server
        :param timeout: time in seconds to wait for the zerodb server to stop
        """
        if not self.container.is_running():
            return

        is_running, job = self.is_running()
        if not is_running:
            return

        logger.debug('stop %s', self)

        self.container.client.job.kill(job['cmd']['id'])

        # wait for zerodb to stop
        start = time.time()
        end = start + timeout
        is_running, _ = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running, _ = self.is_running()

        if is_running:
            raise RuntimeError('Failed to stop zerodb server: {}'.format(self.name))

    def start(self, timeout=15):
        """
        Start zero db server
        :param timeout: time in seconds to wait for the zerodb server to start
        """
        cmd = '/bin/zdb \
            --listen {addr} \
            --port {port} \
            --data {data_dir} \
            --index {index_dir} \
            --sync \
            --mode {mode} \
            '.format(addr=self.addr, port=self.port, data_dir=self.data_dir, index_dir=self.index_dir, mode=self.mode)
        if self.sync:
            cmd += ' --sync'

        # wait for zerodb to start
        self.container.client.system(cmd, id="zerodb.{}".format(self.name))
        start = time.time()
        while start + timeout > time.time():
            if self.container.is_port_listening(self.port):
                break
            time.sleep(1)
        else:
            raise RuntimeError('Failed to start zerodb server: {}'.format(self.name))

    def is_running(self):
        try:
            if self.port not in self.container.node.freeports(self.port, 1):
                for job in self.container.client.job.list():
                    if 'name' in job['cmd']['arguments'] and job['cmd']['arguments']['name'] == '/bin/zdb':
                        return True, job
            return False, None
        except Exception as err:
            if str(err).find("invalid container id"):
                return False, None
            raise
