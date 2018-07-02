from js9 import j

from .JSMainApp import JSMainApp
from gevent.wsgi import WSGIServer
import sys
import os
JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
    host = "localhost"
    port = 5050
    secret_ = ""
    ws_dir = ""
    """


class JSWebServer(JSConfigBase):
    def __init__(self,instance,data={},parent=None,interactive=False,template=None):

        JSConfigBase.__init__(self,instance=instance,data=data,parent=parent,
            template=template or TEMPLATE, interactive=interactive)

        # Set proper instance for j.data.schema

        self.host = self.config.data["host"]
        self.port = int(self.config.data["port"])
        self.address = '{}:{}'.format(self.host, self.port)

        self._inited = False

        self.app = JSMainApp(instance)

        self.http_server = WSGIServer((self.host, self.port), self.app)

        self.app.http_server = self.http_server 

        self.app.server = self

        self.app.load(self.config.data["ws_dir"])


    @property
    def ws_dir(self):
        return self.config.data['ws_dir'].rstrip("/")+"/"

    def scaffold(self, reset=False):

        if not j.sal.fs.exists(self.ws_dir):
            j.sal.fs.createDir(self.ws_dir)

        if not self.ws_dir in sys.path:
            sys.path.append(self.ws_dir)

        j.sal.fs.touch(os.path.join(self.ws_dir, '__init__.py'))

        server_path = os.path.join(self.ws_dir, 'server')
        if not j.sal.fs.exists(server_path):
            j.sal.fs.createDir(server_path)

        if not server_path in sys.path:
            sys.path.append(server_path)

        j.sal.fs.touch(os.path.join(server_path, '__init__.py'))

        # copy the templates in the local server dir
        for item in ["system"]:
            dest = os.path.join(server_path, "%s.py" % item)
            if reset or not j.sal.fs.exists(dest):
                src = os.path.join(j.servers.gedis2._path, "templates", '%s.py' % item)
                j.sal.fs.copyFile(src, dest)
        return server_path

    def sslkeys_generate(self):
        res = j.sal.ssl.ca_cert_generate(self.ws_dir)
        if res:
            self.logger.info("generated sslkeys for gedis in %s" % self.ws_dir)
        else:
            self.logger.info('using existing key and cerificate for gedis @ %s' % self.ws_dir)
        key = os.path.join(self.ws_dir, 'ca.key')
        cert = os.path.join(self.ws_dir, 'ca.crt')
        return key, cert

    def init(self):
        self.logger.info("init server")
        # self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))
        self.logger.info("start server")

        self._inited = True

    def start(self, reset=False):
        print("start")

        self.scaffold(reset=reset)

        if self._inited is False:
            self.init()

        self.http_server.serve_forever()

    def stop(self):
        """
        stop receiving requests and close the server
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        self.logger.info('stopping server')
        self.server.stop()

    def __repr__(self):
        return '<Flask Server address=%s  app_dir=%s)' % (self.address, self.ws_dir)

    __str__ = __repr__