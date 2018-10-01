import time
from jumpscale import j
from .. import templates
from ..abstracts import Nics, Service

logger = j.logger.get(__name__)
DEFAULT_PORT_HTTP = 80
DEFAULT_PORT_HTTPS = 443

class Traefik(Service):
    """
    Traefik a modern HTTP reverse proxy
    """

    def __init__(self, name, node, etcd_endpoint, etcd_watch=True,zt_identity=None, nics=None):
        super().__init__(name, node, 'traefik', [DEFAULT_PORT_HTTP, DEFAULT_PORT_HTTPS])
        self.name = name
        self.id = 'traefik.{}'.format(self.name)
        self.node = node
        self._container = None
        self.flist = 'https://hub.grid.tf/tf-official-apps/traefik-1.7.0-rc5.flist'
        self.etcd_endpoint =etcd_endpoint
        self.etcd_watch = etcd_watch
        self.node_port = None
        
        self._config_dir = '/usr/bin'
        self._config_name = 'traefik.toml'
        self.zt_identity = zt_identity
        self.nics = Nics(self)
        if nics:
            for nic in nics:
                nicobj = self.nics.add(nic['name'], nic['type'], nic['id'], nic.get('hwaddr'))
                if nicobj.type == 'zerotier':
                    nicobj.client_name = nic.get('ztClient')
        if 'nat0' not in self.nics:
            self.nics.add('nat0', 'default')

    @property
    def _container_data(self):
        """
        :return: data used for traefik container
         :rtype: dict
        """
        self.node_port = DEFAULT_PORT_HTTP
        ports = {
            str(DEFAULT_PORT_HTTP): DEFAULT_PORT_HTTP, 
            str(DEFAULT_PORT_HTTPS): DEFAULT_PORT_HTTPS, #HTTPS
        }
        if not self.zt_identity:
            self.zt_identity = self.node.client.system('zerotier-idtool generate').get().stdout.strip()
        zt_public = self.node.client.system('zerotier-idtool getpublic {}'.format(self.zt_identity)).get().stdout.strip()
        j.sal_zos.utils.authorize_zerotiers(zt_public, self.nics)

        return {
            'name':  self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [nic.to_dict(forcontainer=True) for nic in self.nics],
            'identity': self.zt_identity,
        }

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

    def container_port(self, port):
        return self._container.get_forwarded_port(port)

    def create_config(self):
        logger.info('Creating traefik config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):
        etcd_url=self.etcd_endpoint.split('http://')
        return templates.render(
            'traefik.conf', etcd_ip =etcd_url[1]).strip()

    def is_running(self):
        try:
            for _ in self.container.client.job.list(self.id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def start(self, timeout=15):
        """
        Start traefik
        :param timeout: time in seconds to wait for the traefik to start
        """
        is_running = self.is_running()
        if is_running:
            return

        logger.info('start traefik %s' % self.name)

        self.create_config()

        cmd = '/usr/bin/traefik -c {dir}/{config}'.format(dir=self._config_dir,config=self._config_name)
       
        # wait for traefik to start
        self.container.client.system(cmd, id=self.id)
        if j.tools.timer.execute_until(self.is_running, timeout, 0.5):
            return True

        if not is_running:
            raise RuntimeError('Failed to start traefik server: {}'.format(self.name))

    def stop(self, timeout=30):
        """
        Stop the traefik
        :param timeout: time in seconds to wait for the traefik gateway to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.info('stop traefik %s' % self.name)

        self.container.client.job.kill(self.id)

        # wait for traefik to stop
        if j.tools.timer.execute_until(self.is_running, timeout, 0.5):
            return True

        if is_running:
            raise RuntimeError('Failed to stop traefik server: {}'.format(self.name))

        self.container.stop()

    def destroy(self):
        self.stop()
        self.container.stop()