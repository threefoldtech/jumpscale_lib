import logging
import time
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TfChain:
    """
    TfChain server
    """

    def __init__(self, name, container, wallet_passphrase, data_dir='/mnt/data',
                 rpc_addr='0.0.0.0:23112', api_addr='localhost:23110'):
        self.name = name
        self.id = 'tfchain.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr
        self._daemon = None
        self._client = None
        self.wallet_passphrase = wallet_passphrase

    @property
    def daemon(self):
        if self._daemon is None:
            self._daemon = TfChainDaemon(
                name=self.name,
                container=self.container,
                data_dir=self.data_dir,
                rpc_addr=self.rpc_addr,
                api_addr=self.api_addr,
            )
        return self._daemon

    @property
    def client(self):
        if self._client is None:
            self._client = TfChainClient(
                name=self.name,
                container=self.container,
                addr=self.api_addr,
                wallet_passphrase=self.wallet_passphrase,
            )
        return self._client


class TfChainDaemon:
    """
    TfChain Daemon
    """

    def __init__(self, name, container, data_dir='/mnt/data',
                 rpc_addr='localhost:23112', api_addr='localhost:23110'):
        self.name = name
        self.id = 'tfchaind.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr

    def start(self, timeout=150):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        is_running = self.is_running()
        if is_running:
            return

        cmd_line = '/bin/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --tfchain-directory {data_dir} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir)

        cmd = self.container.client.system(cmd_line, id=self.id)

        port = int(self.api_addr.split(":")[1])
        while not self.container.is_port_listening(port, timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start tfchaind.\nstdout: %s\nstderr: %s" % (
                    result.stdout, result.stderr))

    def stop(self, timeout=30):
        """
        Stop the tfchain daemon
        :param timeout: time in seconds to wait for the daemon to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.debug('stop %s', self)
        self.container.stop_job(self.id, signal=signal.SIGINT, timeout=timeout)

    def is_running(self):
        return self.container.is_job_running(self.id)


class TfChainClient:
    """
    TfChain Client
    """

    def __init__(self, name, container, wallet_passphrase, addr='localhost:23110'):
        self.name = name
        self.id = 'tfchainc.{}'.format(self.name)
        self.container = container
        self.addr = addr
        self._recovery_seed = None
        self._wallet_address = None
        self._wallet_password = wallet_passphrase

    @property
    def recovery_seed(self):
        return self._recovery_seed

    @property
    def wallet_password(self):
        return self._wallet_password

    @property
    def wallet_address(self):
        if self._wallet_address is None:
            cmd = '/bin/tfchainc --addr {} wallet address'.format(self.addr)
            result = self.container.client.bash(cmd, id='%s.wallet_init' % self.id).get()

            if result.state != 'SUCCESS':
                raise RuntimeError("Could not initialize wallet.\nstdout: %s\nstderr: %s" % (
                        result.stdout, result.stderr))

            self._wallet_address = result.stdout.split('Created new address: ')[-1].strip()

        return self._wallet_address

    def wallet_init(self):
        cmd = '(echo "{0}" && echo "{0}") | /bin/tfchainc --addr {1} wallet init'.format(self.wallet_password, self.addr)
        result = self.container.client.bash(cmd, id='%s.wallet_init' % self.id).get()

        if result.state != 'SUCCESS':
            raise RuntimeError("Could not initialize wallet.\nstdout: %s\nstderr: %s" % (
                    result.stdout, result.stderr))

        self._recovery_seed = result.stdout.split('Recovery seed:\n')[-1].split('\n\nWallet encrypted with given passphrase\n')[0].strip()

    def wallet_unlock(self):
        cmd = 'echo "%s" | /bin/tfchainc --addr %s wallet unlock' % (self.wallet_password, self.addr)
        response = self.container.client.bash(cmd, id='%s.wallet_unlock' % self.id)

        result = response.get()
        if result.state != 'SUCCESS':
            raise RuntimeError("Could not unlock wallet.\nstdout: %s\nstderr: %s" % (
                    result.stdout, result.stderr))


class TfChainExplorer:
    """
    TfChain Explorer
    """

    def __init__(self, name, container):
        self.name = name
        self.id = 'tfchainc.{}'.format(self.name)
        self.container = container

    def start(self, timeout=15):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        is_running = self.is_running()
        if is_running:
            return

        cmd_line = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --tfchain-directory {data_dir} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir)

        cmd = self.container.client.system(cmd_line, id=self.id)

        # wait for tfchain daemon to start
        start = time.time()
        while not self.container.is_port_listening(int(self.api_addr.split(":")[1]), timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start tfchain explorer.\nstdout: %s\nstderr: %s" % (
                    result.stdout, result.stderr))
            if time.time() > start + timeout:
                self.container.client.job.kill(self.id, signal=9)
                result = cmd.get()
                raise RuntimeError("tfchain explorer failed to start within %s seconds!\nstdout: %s\nstderr: %s", (
                    timeout, result.stdout, result.stdout))
