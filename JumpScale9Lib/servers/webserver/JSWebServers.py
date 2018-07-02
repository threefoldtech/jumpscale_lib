

import os

from js9 import j

from .JSWebServer import JSWebServer

JSConfigBase = j.tools.configmanager.base_class_configs


class JSWebServers(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.web"

        JSConfigBase.__init__(self, JSWebServer)

    def configure(self, instance="main", port=5050, host="localhost", secret="", ws_dir=""):
        """
        js9 'j.servers.web.configure()'

        """
        if ws_dir is "":
            ws_dir = j.sal.fs.getcwd()

        data = {
            "port": port,
            "host": host,
            "secret_": secret,
            "ws_dir": ws_dir,
        }

        return self.get(instance, data)

    def install(self):
        """
        js9 'j.servers.web.install()'

        """        
        p = j.tools.prefab.local
        p.runtimes.pip.install("rq-dashboard,rq-scheduler,rq,flask-classy")  # ,Flask-Bootstrap4")

    def start(self, instance="main",background=False):

        # start redis
        print("make sure core redis running")
        j.clients.redis.core_check()

        s=self.get(instance)

        if not background:
            s.start()
        else:
            # start
            cmd = """
            export LC_ALL=de_DE.utf-8
            export LANG=de_DE.utf-8
            export FLASK_DEBUG=1
            export APP_SETTINGS=project.server.config.DevelopmentConfig
            js9_web start -i $instance       
            """
            cmd = cmd.replace("$instance", instance)
            j.tools.tmux.execute(cmd, session='main', window=instance, pane='main', session_reset=False, window_reset=True)

            host =  s.config.data["host"]
            port =  s.config.data["port"]
            print("webserver running on http://%s:%s/"%(host,port))
