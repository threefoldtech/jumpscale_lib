from .server.app import app

from js9 import j

TEMPLATE = """
host = "localhost"
port = 9900
debug = false
"""
JSConfigBase = j.tools.configmanager.base_class_config


class CapacityServer(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False, template=None):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self.app = app

    def start(self):
        self.app.run(host=self.config.data['host'], port=self.config.data['port'], debug=self.config.data['debug'])
