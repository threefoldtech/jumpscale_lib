

import os

from js9 import j

from .JSWebServer import JSWebServer

JSConfigBase = j.tools.configmanager.base_class_configs


class JSWebServers(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.web"

        JSConfigBase.__init__(self, JSWebServer)

    def configure(self, instance="main", port=5050,port_ssl=0, host="localhost", secret="", ws_dir=""):
        """
        params
            - port_ssl if 0 not used

        js9 'j.servers.web.configure()'

        """
        if ws_dir is "":
            ws_dir = j.sal.fs.getcwd()

        config_path = j.sal.fs.joinPaths(ws_dir,"site_config.toml")
        if not j.sal.fs.exists(config_path):
            raise RuntimeError("cannot find: %s"%config_path)

        data = {
            "port": port,
            "port_ssl": port_ssl,
            "host": host,
            "secret_": secret,
            "ws_dir": ws_dir,
        }

        return self.get(instance, data, interactive=False)

    def install(self):
        """
        js9 'j.servers.web.install()'

        """        
        pips="""
        flask
        flask_login
        flask_migrate
        flask_wtf
        flask_sqlalchemy
        gunicorn
        gevent
        """
        #rq-dashboard,rq-scheduler,rq,flask-classy,
        p = j.tools.prefab.local
        p.runtimes.pip.install(pips)  # ,Flask-Bootstrap4")

    def start(self, instance="main",background=False, debug=False):

        # start redis
        print("make sure core redis running")
        j.clients.redis.core_check()

        s=self.get(instance)

        if not background:
            s.start(debug=debug)
        else:
            # start
            cmd = """
            export LC_ALL=de_DE.utf-8
            export LANG=de_DE.utf-8
            export FLASK_DEBUG=1
            export APP_SETTINGS=project.server.config.DevelopmentConfig
            js9_web start -i $instance -d    
            """
            cmd = cmd.replace("$instance", instance)
            j.tools.tmux.execute(cmd, session='main', window=instance, pane='main', session_reset=False, window_reset=True)

            host =  s.config.data["host"]
            port =  s.config.data["port"]
            print("webserver running on http://%s:%s/"%(host,port))
