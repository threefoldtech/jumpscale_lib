from js9 import j

from influxdb import client as influxdb
import requests
from requests.auth import HTTPBasicAuth

JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
host = ""
port = 8086
username = "root"
password = ""
database = ""
ssl = false
verify_ssl = false
timeout = ""
use_udp = false
udp_port = 4444
"""




class InfluxdbFactory(JSConfigFactory):

    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.influxdb"
        self.__imports__ = "influxdb"
        JSConfigFactory.__init__(self, InfluxClient)


    def postraw(self, data, host='localhost', port=8086, username='root', password='root', database="main"):
        """
        format in is
        '''
        hdiops,machine=unit42,datacenter=gent,type=new avg=25,max=37 1434059627
        temperature,machine=unit42,type=assembly external=25,internal=37 1434059627
        '''

        """
        url = 'http://%s:%s/write?db=%s&precision=s' % (host, port, database)
        r = requests.post(
            url, data=data, auth=HTTPBasicAuth(username, password))
        if r.content != "":
            raise j.exceptions.RuntimeError(
                "Could not send data to influxdb.\n%s\n############\n%s" % (data, r.content))

class InfluxClient(JSConfigClient, influxdb.InfluxDBClient):

    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        influxdb.InfluxDBClient.__init__(
            self,
            host=c.get('host', 'localhost'),
            port=c.get('port', 8086),
            username=c.get('username', 'root'),
            password=c.get('password', None),
            database=c.get('database', None),
            ssl=c.get('ssl', False),
            verify_ssl=c.get('verify_ssl', False),
            timeout=c.get('timeout', None),
            use_udp=c.get('use_udp', False),
            udp_port=c.get('udp_port', 4444))