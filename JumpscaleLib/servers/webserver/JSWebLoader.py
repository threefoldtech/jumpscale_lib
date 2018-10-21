from flask import Flask
from flask_login import LoginManager
from flask import  url_for,redirect
from flask_sockets import Sockets
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from Jumpscale import j
import sys


JSBASE = j.application.JSBaseClass


class Config(object):
    SECRET_KEY = 'key'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


class DebugConfig(Config):
    DEBUG = True


class JSWebLoader(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)
        # self.db = SQLAlchemy()
        self.login_manager = LoginManager()
        self.paths = []
        self.app = None

    def register_blueprints(self, sockets, paths):
        for path in paths:
            ppath = '/'.join(path.split('/')[:-1])
            if ppath not in sys.path:
                sys.path.append(ppath)
            apps = j.sal.fs.listDirsInDir(path, recursive=False, dirNameOnly=True,
                                          findDirectorySymlinks=True, followSymlinks=True)
            apps = [item for item in apps if item[0] is not "_"]
            for module_name in apps:
                try:
                    module = import_module('blueprints.{}.routes'.format(module_name))
                    print("blueprint register:%s" % module_name)
                    self.app.register_blueprint(module.blueprint)
                    if sockets and hasattr(module, "ws_blueprint"):
                        sockets.register_blueprint(module.ws_blueprint)
                except Exception as e:
                    # TODO: errors should be handled correctly, this is temp thing till we finish fixing gedis and docsites
                    print(e)
                    print("%s not loaded due to an error" % module_name)

    def _configure_database(self):

        @app.before_first_request
        def initialize_database():
            self.db.create_all()

        @app.teardown_request
        def shutdown_session(exception=None):
            self.db.session.remove()

    def _configure_logs(self):
        # TODO: why can we not use jumpscale logging?
        basicConfig(filename='error.log', level=DEBUG)
        self.logger = getLogger()
        self.logger.addHandler(StreamHandler())

    def load(self, selenium=False, debug=True, websocket_support=True):
        staticpath = j.clients.git.getContentPathFromURLorPath(
            "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/static")
        app = Flask(__name__, static_folder=staticpath)  # '/base/static'
        app.config.from_object(DebugConfig)

        # Load iyo settings, TODO: change this dirty hack & re-enable this section
        # sys.path.append("%s/dm_base" % self.path)
        # app.config.from_json("%s/dm_base/blueprints/user/iyo.json" % self.path)
        # from blueprints.user.user import callback
        # app.add_url_rule(app.config['IYO_CONFIG']['callback_path'], '_callback', callback)

        # if selenium:
        #     app.config['LOGIN_DISABLED'] = True


        # self.db.init_app(app)
        self.login_manager.init_app(app)

        sockets = None
        if websocket_support:
            sockets = Sockets(app)

        self.app = app
        self.register_blueprints(sockets, self.paths)

        def redirect_wiki(*args,**kwargs):
            return redirect("wiki/")

        self.app.add_url_rule("/", "index",redirect_wiki)


        print(app.url_map)
