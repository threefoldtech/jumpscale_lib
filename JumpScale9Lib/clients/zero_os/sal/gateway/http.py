import signal
import time

from .. import templates
from js9 import j

class HTTPServer():
    def __init__(self, container, httpproxies, type):
        self.container = container
        self.httpproxies = httpproxies
        self.type = type

    def id(self):
        return 'http.{}'.format(self.container.name)

    def apply_rules(self):
        # caddy
        caddyconfig = templates.render('caddy.conf', type=self.type, httpproxies=self.httpproxies).strip()
        conf = '/etc/caddy-{}.conf'.format(self.type)
        self.container.upload_content(conf, caddyconfig)
        self.container.client.job.kill(self.id(), int(signal.SIGUSR1))
        if caddyconfig == '':
            return
        job = self.container.client.system(
            'caddy -agree -conf {}'.format(conf), stdin='\n', id=self.id())
        start = time.time()
        while start + 10 > time.time():
            if self.is_running():
                return True
            time.sleep(0.5)
        if not job.running:
            result = job.get()
            raise RuntimeError("Failed to start caddy server: {} {} {}".format(result.stderr, result.stdout, result.data))
        self.container.client.job.kill(job.id)
        raise RuntimeError("Failed to start caddy server: didnt start listening")

    def is_running(self):
        try:
            self.container.client.job.list(self.id())
        except:
            return False
        portnr = 80 if self.type == 'http' else 443
        for port in self.container.client.info.port():
            if port['network'] .startswith('tcp') and port['port'] == portnr:
                return True
        return False
