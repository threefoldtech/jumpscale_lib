import time
from jumpscale import j
from .. import templates


logger = j.logger.get(__name__)
DEFAULT_PORT = 9700

class Traefik:
    """
    Traefik a modern HTTP reverse proxy
    """

    def __init__(self, name, node, etcd_endpoint, etcd_watch=True):
        
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

    @property
    def _container_data(self):
        """
        :return: data used for traefik container
         :rtype: dict
        """
        ports = self.node.freeports(1)
        if len(ports) <= 0:
            raise RuntimeError("can't install traefik, no free port available on the node")

        self.node_port = ports[0]
        ports = {
            str(ports[0]): self.node_port,
        }

        return {
            'name': self._container_name,
            'flist': self.flist,
            'ports': ports,
            'nics': [{'type': 'default'}],
        }

    @property
    def _container_name(self):
        """
        :return: name used for traefik container
        :rtype: string
        """
        return 'traefik_{}'.format(self.name)

    @property
    def container(self):
        """
        Get/create traefik container to run traefik services on
        :return: traefik container
        :rtype: container sal object
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self._container_name)
            except LookupError:
                self._container = self.node.containers.create(**self._container_data)
        return self._container

    def create_config(self):
        logger.info('Creating traefik config for %s' % self.name)
        config = self._config_as_text()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)

    def _config_as_text(self):
        
        return templates.render(
            'traefik.conf', etcd_ip =self.etcd_endpoint).strip()

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

        cmd = '/usr/bin/traefik ./traefik  -c {dir}/{config}'.format(dir=self._config_dir,config=self._config_name)
       
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
    
    def key_value_storage(self,url_backend ,url_frontend):
        logger.info('updating your traefik config')
        file_conf = self.container.client.filesystem.open('{dir}/{config}'.format(dir=self._config_dir,config=self._config_name), 'r')
        data = self.container.client.filesystem.read(file_conf)
        routes_name = url_frontend.split('.')
        
        data_parse = j.data.serializer.toml.loads(data)
        data_parse['backends'].update({'backend%s' % len(str(data)) :{'servers':{'server1':{'url':'%s:80' % url_backend , 'weight':'10'}}}})
        data_parse['frontends'].update({'frontend%s' % len(str(data)) :{'routes':{'%s' % routes_name[0]:{'rule':'Host:%s' % url_frontend }}}})
        self.container.client.filesystem.remove('{dir}/{config}'.format(dir=self._config_dir,config=self._config_name))
        
        data_dumps = j.data.serializer.toml.dumps(data_parse)
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), data_dumps)
        logger.info('update your traefik config')
