from Jumpscale import j
from gevent.pywsgi import WSGIServer
# from geventwebsocket.handler import WebSocketHandler
from flask import Flask
# from flask_login import LoginManager
from flask import  url_for,redirect
from flask_sockets import Sockets
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
import sys
import os


JSConfigBase = j.tools.configmanager.JSBaseClassConfig

TEMPLATE = """
    host = "localhost"
    port = 5050
    port_ssl = 0
    secret_ = ""
    ws_dir = ""
    """



class JSWebServer(JSConfigBase):
    def __init__(self, instance, data=None, parent=None, interactive=False, template=None):
        if not data:
            data = {}
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=template or TEMPLATE, interactive=interactive)

        # Set proper instance for j.data.schema
        self.host = self.config.data["host"]
        self.port = int(self.config.data["port"])
        self.port_ssl = int(self.config.data["port_ssl"])
        self.address = '{}:{}'.format(self.host, self.port)

        # self.login_manager = LoginManager()
        self.paths = []
        self.app = None  #flask app
        self.websocket = None

        self._inited = False

        j.servers.web.latest = self
        self.http_server = None

        self.path_blueprints = j.sal.fs.joinPaths(j.dirs.VARDIR,"dm_packages","blueprints")

        self.logger_enable()


    def sslkeys_generate(self):
        res = j.sal.ssl.ca_cert_generate(self.ws_dir)
        if res:
            self.logger.info("generated sslkeys for gedis in %s" % self.ws_dir)
        else:
            self.logger.info('using existing key and cerificate for gedis @ %s' % self.ws_dir)
        key = os.path.join(self.path, 'ca.key')
        cert = os.path.join(self.path, 'ca.crt')
        return key, cert

    def start(self, debug=False):
        self.logger.info("start")
        self._init(debug=debug)

        self._register_blueprints()
        self.logger.info("%s"%self)
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))
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


    def _register_blueprints(self):

        self.logger.info("register blueprints")

        j.shell()
        if self.path_blueprints not in sys.path:
            sys.path.append(self.path_blueprints)

            # if not j.sal.fs.getBaseName(src2).startswith("_"):
            #     j.servers.web.latest.loader.paths.append(src2)

        for path in paths:
            module_name = j.sal.fs.getBaseName(path)
            j.shell()
            module = import_module('%s.routes'%module_name)
            print("blueprint register:%s" % module_name)
            self.app.register_blueprint(module.blueprint)
            if self.sockets and hasattr(module, "ws_blueprint"):
                self.sockets.register_blueprint(module.ws_blueprint)

    # def _configure_database(self):
    #
    #     @app.before_first_request
    #     def initialize_database():
    #         self.db.create_all()
    #
    #     @app.teardown_request
    #     def shutdown_session(exception=None):
    #         self.db.session.remove()

    def _configure_logs(self):
        # TODO: why can we not use jumpscale logging?
        basicConfig(filename='error.log', level=DEBUG)
        self.logger = getLogger()
        self.logger.addHandler(StreamHandler())

    def _init(self, selenium=False, debug=True, websocket_support=True):

        if self._inited:
            return

        class Config(object):
            SECRET_KEY = 'js007'

        class ProductionConfig(Config):
            DEBUG = False

        class DebugConfig(Config):
            DEBUG = True


        staticpath = j.clients.git.getContentPathFromURLorPath(
            "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/static")
        app = Flask(__name__, static_folder=staticpath)  # '/base/static'

        if debug:
            app.config.from_object(DebugConfig)
        else:
            app.config.from_object(ProductionConfig)

        # Load iyo settings, TODO: change this dirty hack & re-enable this section
        # sys.path.append("%s/dm_base" % self.path)
        # app.config.from_json("%s/dm_base/blueprints/user/iyo.json" % self.path)
        # from blueprints.user.user import callback
        # app.add_url_rule(app.config['IYO_CONFIG']['callback_path'], '_callback', callback)

        # if selenium:
        #     app.config['LOGIN_DISABLED'] = True


        # self.db.init_app(app)
        # self.login_manager.init_app(app)

        if websocket_support:
            self.sockets = Sockets(app)

        self.app = app

        def redirect_wiki(*args,**kwargs):
            return redirect("wiki/")

        self.app.add_url_rule("/", "index",redirect_wiki)

        #double with above
        self.app.debug = True

        self.http_server = WSGIServer((self.host, self.port), self.app, handler_class=WebSocketHandler)
        self.app.http_server = self.http_server
        self.app.server = self


        self._inited = True

    def __repr__(self):
        return '<Flask Server http://%s:%s)' % (self.address, self.port)

    __str__ = __repr__
