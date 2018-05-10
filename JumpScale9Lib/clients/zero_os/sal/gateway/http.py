from js9 import j
import signal
from .. import templates

class HTTPServer():
    def __init__(self, container, httpproxies, type):
        self.container = container
        self.httpproxies = httpproxies
        self.type = type

    def id(self):
        return '{}.{}'.format(self.type, self.container.name)

    def apply_rules(self):
        # caddy
        caddyconfig = templates.render('caddy.conf', type=self.type, httpproxies=self.httpproxies).strip()
        conf = '/etc/caddy-{}.conf'.format(self.type)
        self.container.upload_content(conf, caddyconfig)
        self.container.client.job.kill(self.id(), int(signal.SIGUSR1))
        if caddyconfig == '':
            return
        args = ''
        if self.type == 'https':
            args = '-http-port 81'
        job = self.container.client.system(
            'caddy -disable-http-challenge {} -agree -conf {}'.format(args, conf), stdin='\n', id=self.id())
        if j.tools.timer.execute_until(self.is_running, 30, 0.5):
            return True
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
        return self.container.is_port_listening(portnr, 0)
