from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sockets import Sockets
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from jumpscale import j
import sys
from werkzeug.debug import DebuggedApplication
import rq_dashboard

JSBASE = j.application.jsbase_get_class()


class Config(object):
    SECRET_KEY = 'key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


class DebugConfig(Config):
    DEBUG = True


class JSWebLoader(JSBASE):
    def __init__(self, path):
        JSBASE.__init__(self)
        self.db = SQLAlchemy()
        self.path = path
        self._init_app()
        self.login_manager = LoginManager()
        # self._configure_database()
        # self._configure_logs(app)

    def register_blueprints(self, sockets, path=None):
        if path is None:
            path = "%s/dm_base/blueprints" % self.path
        if path not in sys.path:
            sys.path.append(path)
        apps = j.sal.fs.listDirsInDir(path, recursive=False, dirNameOnly=True,
                                      findDirectorySymlinks=True, followSymlinks=True)
        apps = [item for item in apps if item[0] is not "_"]
        for module_name in apps:
            module = import_module('blueprints.{}.routes'.format(module_name))
            print("blueprint register:%s" % module_name)
            # try:
            #     module = import_module('blueprints.{}.routes'.format(module_name))
            #     print("blueprint register:%s" % module_name)
            # except Exception as e:
            #     print("WARNING: could not load required libraries for the HUB blueprint")
            #     print(e)

            self.app.register_blueprint(module.blueprint)
            if sockets and hasattr(module, "ws_blueprint"):
                sockets.register_blueprint(module.ws_blueprint)

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

    # def app_load(self, app, selenium=False):
    #     # app = Flask(__name__, static_folder='base/static')
    #     app.config.from_object(DebugConfig)

    #     app.config.from_object(rq_dashboard.default_settings)
    #     app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    #     # if selenium:
    #     #     app.config['LOGIN_DISABLED'] = True
    #     # register_extensions(app)
    #     self.register_blueprints(app)
    #     # configure_database(app)
    #     # configure_logs(app)

    #     return app

    def _init_app(self, selenium=False, debug=True, websocket_support=True):
        staticpath = j.clients.git.getContentPathFromURLorPath(
            "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/static")
        app = Flask(__name__, static_folder=staticpath)  # '/base/static'
        app.config.from_object(DebugConfig)

        app.config.from_object(rq_dashboard.default_settings)
        app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

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

        self.register_blueprints(app, sockets)
        print(app.url_map)

        if debug is True:
            app = DebuggedApplication(app, evalex=True)

        self.app = app
