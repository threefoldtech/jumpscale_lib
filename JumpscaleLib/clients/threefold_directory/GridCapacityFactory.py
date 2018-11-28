from jumpscale import j
from dateutil import parser
import time

from .api_service import ApiService

from .http_client import HTTPClient

JSBASE = j.application.jsbase_get_class()
JSConfigClient = j.tools.configmanager.base_class_config
JSConfigFactory = j.tools.configmanager.base_class_configs
TEMPLATE = """
base_uri = "https://capacity.threefoldtoken.com"
"""


class Client(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        super().__init__(instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        http_client = HTTPClient(self.config.data['base_uri'])
        self.api = ApiService(http_client)
        self.close = http_client.close


class GridCapacityFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.threefold_directory"
        self.connections = {}
        self._api = None
        JSConfigFactory.__init__(self, Client)

    @property
    def client(self):
        if self._api is None:
            self.configure(instance="main")
            self._api = self.get().api
        return self._api

    @property
    def _capacity(self):
        def do():
            items = []

            for item in self.client.ListCapacity()[0]:
                x = item.as_dict()

                # convert datetime to timestamp
                if x['updated']:
                    dt = parser.parse(x['updated']).replace(tzinfo=None)
                    ts = int(time.mktime(dt.timetuple()))
                    x['updated'] = ts

                items.append(x)

            return items

        return self.cache.get("_capacity", method=do, expire=60)

    @property
    def capacity(self):
        """
        is cached for 60 sec
        """
        return self._capacity

    def configure(self, instance, base_uri="https://capacity.threefoldtoken.com", interactive=False):
        """
        :param base_uri: Url for grid_capacity api
        :type base_uri: str
        """
        data = {}
        data["base_uri"] = base_uri
        return self.get(instance=instance, data=data, interactive=interactive)

    def resource_units(self, reload=False):
        """
        js_shell "print(j.clients.threefold_directory.resource_units())"
        """
        if reload:
            self.cache.reset()
        nodes = self._capacity

        resource_units = {
            'cru': 0,
            'mru': 0,
            'hru': 0,
            'sru': 0,
        }

        for node in nodes:
            resource_units['cru'] += node['total_resources']['cru']
            resource_units['mru'] += node['total_resources']['mru']
            resource_units['hru'] += node['total_resources']['hru']
            resource_units['sru'] += node['total_resources']['sru']

        return(resource_units)
