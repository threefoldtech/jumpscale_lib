from jumpscale import j
from .server import settings, influxdb

TEMPLATE = """
host = "localhost"
port = 9900
debug = false
iyo_clientid = ""
iyo_secret = ""
iyo_callback = ""
influx_host = ""
influx_port = 8086
influx_db = ''
"""
JSConfigBase = j.tools.configmanager.base_class_config


class CapacityServer(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False, template=None):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)

        settings.HOST = self.config.data['host']
        settings.PORT = self.config.data['port']
        settings.DEBUG = self.config.data['debug']
        settings.IYO_CLIENTID = self.config.data['iyo_clientid']
        settings.IYO_SECRET = self.config.data['iyo_secret']
        settings.IYO_CALLBACK = self.config.data['iyo_callback']
        settings.INFLUX_HOST = self.config.data['influx_host']
        settings.INFLUX_PORT = self.config.data['influx_port']
        settings.INFLUX_DB = self.config.data['influx_db']

        from .server.app import app
        self.app = app

    def start(self):
        if settings.INFLUX_HOST and settings.INFLUX_DB:
            influxdb.init(settings.INFLUX_HOST, settings.INFLUX_PORT, settings.INFLUX_DB)

        self.app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
