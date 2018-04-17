import logging
import time
import signal
from . import templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TfChain:

    def daemon(self, name, container, data_dir='/mnt/data', rpc_addr='0.0.0.0:23112', api_addr='localhost:23110', network='standard'):
        return TfChainDaemon(name=name, container=container, data_dir=data_dir, rpc_addr=rpc_addr, api_addr=api_addr, network=network)

    def explorer(self, name, container, domain, data_dir='/mnt/data', rpc_addr='0.0.0.0:23112', api_addr='localhost:23110', network='standard'):
        return TfChainExplorer(name=name, container=container, data_dir=data_dir, rpc_addr=rpc_addr, api_addr=api_addr, domain=domain, network=network)

    def client(self, name, container, wallet_passphrase, api_addr='localhost:23110'):
        return TfChainClient(name=name, container=container, addr=api_addr, wallet_passphrase=wallet_passphrase)


class TfChainDaemon:
    """
    TfChain Daemon
    """

    def __init__(self, name, container, data_dir='/mnt/data', rpc_addr='localhost:23112', api_addr='localhost:23110', network='standard'):
        self.name = name
        self.id = 'tfchaind.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr
        self.network = network

    def start(self, timeout=150):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        if self.is_running():
            return

        cmd_line = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --persistent-directory {data_dir} \
            --network {network} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir,
                     network=self.network)

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
        if not self.is_running():
            return

        logger.debug('stop %s', self)
        self.container.stop_job(self.id, signal=signal.SIGINT, timeout=timeout)

    def is_running(self):
        return self.container.is_job_running(self.id)


class TfChainExplorer:
    """
    TfChain Explorer Daemon
    """

    def __init__(self, name, container, domain, data_dir='/mnt/data', rpc_addr='localhost:23112', api_addr='localhost:23110', network='standard'):
        self.name = name
        self.domain = domain
        self.tf_ps_id = 'tfchaind.{}'.format(self.name)
        self.caddy_ps_id = 'caddy.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr
        self.network = network

    def start(self, timeout=30):
        """
        Start tfchain explorer daemon and caddy as reverse proxy
        :param timeout: time in seconds to wait for the both process to start
        """
        self._start_tf_deamon(timeout=timeout)
        self._start_caddy(timeout=timeout)

    def _start_tf_deamon(self, timeout=150):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        if self.is_running():
            return

        cmd_line = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --persistent-directory {data_dir} \
            --modules gcte \
            --network {network} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir,
                     network=self.network)

        cmd = self.container.client.system(cmd_line, id=self.tf_ps_id)

        port = int(self.api_addr.split(":")[1])
        while not self.container.is_port_listening(port, timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start tfchaind.\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))

    def _start_caddy(self, timeout=150):
        """
        Start caddy
        :param timeout: time in seconds to wait for caddy to start
        """
        if self.is_running():
            return

        logger.info('Creating caddy config for %s' % self.name)
        config_location = '/mnt/explorer/explorer/caddy/Caddyfile'
        config = templates.render('tf_explorer_caddy.conf', domain=self.domain)
        self.container.upload_content(config_location, config)

        cmd_line = '/mnt/explorer/bin/caddy -conf %s' % config_location
        cmd = self.container.client.system(cmd_line, id=self.caddy_ps_id)

        port = 443
        while not self.container.is_port_listening(port, timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start caddy.\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))

    def stop(self, timeout=30):
        """
        Stop the tfchain daemon
        :param timeout: time in seconds to wait for the daemon to stop
        """
        self._stop_caddy_daemon(timeout)
        self._stop_tf_daemon(timeout)

    def _stop_tf_daemon(self, timeout=30):
        if not self._is_tf_running():
            return

        logger.debug('stop tf daemon %s', self)
        self.container.stop_job(self.tf_ps_id, signal=signal.SIGINT, timeout=timeout)

    def _stop_caddy_daemon(self, timeout=30):
        if not self._is_caddy_running():
            return

        logger.debug('stop caddy %s', self)
        self.container.stop_job(self.caddy_ps_id, signal=signal.SIGINT, timeout=timeout)

    def is_running(self):
        return self._is_tf_running() and self._is_caddy_running()

    def _is_tf_running(self):
        return self.container.is_job_running(self.tf_ps_id)

    def _is_caddy_running(self):
        return self.container.is_job_running(self.caddy_ps_id)

    def consensus_stat(self):
        return consensus_stat(self.container, self.api_addr)

    def gateway_stat(self):
        return gateway_stat(self.container, self.api_addr)


class TfChainClient:
    """
    TfChain Client
    """

    def __init__(self, name, container, wallet_passphrase, addr='localhost:23110'):
        self.name = name
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
            cmd = '/tfchainc --addr {} wallet address'.format(self.addr)
            result = self.container.client.bash(cmd).get()

            if result.state != 'SUCCESS':
                raise RuntimeError("Could not get wallet address: %s" % result.stderr.splitlines()[-1])

            self._wallet_address = result.stdout.split('Created new address: ')[-1].strip()

        return self._wallet_address

    def wallet_init(self):
        cmd = '/tfchainc --addr %s wallet init' % self.addr
        result = self.container.client.system(cmd, stdin='{0}\n{0}'.format(self.wallet_password)).get()

        if result.state != 'SUCCESS':
            raise RuntimeError("Could not initialize wallet: %s" % result.stderr.splitlines()[-1])

        self._recovery_seed = result.stdout.split('Recovery seed:\n')[-1].split('\n\nWallet encrypted with given passphrase\n')[0].strip()

    def wallet_unlock(self):
        cmd = '/tfchainc --addr %s wallet unlock' % self.addr
        result = self.container.client.system(cmd, stdin=self.wallet_password).get()
        if result.state != 'SUCCESS':
            raise RuntimeError("Could not unlock wallet: %s" % result.stderr.splitlines()[-1])

    def wallet_amount(self):
        """
        return the amount of token and block stake in the wallet
        """
        cmd = '/tfchainc --addr %s wallet' % self.addr
        result = self.container.client.system(cmd).get()
        if result.state != 'SUCCESS':
            raise RuntimeError("Could not get wallet amount: %s" % result.stderr.splitlines()[-1])

        args = {}
        for line in result.stdout.splitlines()[2:]:
            k, v = line.split(':')
            k = k.strip()
            v = v.strip()
            args[k] = v
        return args
    
    def wallet_status(self):
        """
        return the status of the wallet [locked/unlocked]
        """
        cmd = '/tfchainc --addr %s wallet' % self.addr
        result = self.container.client.system(cmd).get()
        if result.state != 'SUCCESS':
            raise RuntimeError("Could not get wallet status: %s" % result.stderr.splitlines()[-1])
        
        return "locked" if "Locked" in result.stdout else "unlocked"

    def consensus_stat(self):
        return consensus_stat(self.container, self.addr)


def consensus_stat(container, addr):
    cmd = '/tfchainc --addr %s consensus' % addr
    result = container.client.system(cmd).get()
    if result.state != 'SUCCESS':
        raise RuntimeError("Could not unlock wallet: %s" % result.stderr.splitlines()[-1])
    stats = {}
    for line in result.stdout.splitlines():
        ss = line.split(':')
        stats[ss[0].strip()] = ss[1].strip()
    return stats


def gateway_stat(container, addr):
    cmd = '/tfchainc --addr %s gateway' % addr
    result = container.client.system(cmd).get()
    if result.state != 'SUCCESS':
        raise RuntimeError("Could not unlock wallet: %s" % result.stderr.splitlines()[-1])
    stats = {}
    for line in result.stdout.splitlines():
        ss = line.split(':')
        stats[ss[0].strip()] = ss[1].strip()
    return stats
