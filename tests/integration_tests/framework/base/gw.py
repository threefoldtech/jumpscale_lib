from jumpscale import j
import copy
from termcolor import colored


class GW:

    def __init__(self, node, data=None):
        self.data = data
        self.node_sal = node
        self.gw_sal = None

    def validate(self):
        if not self.data['hostname']:
            raise ValueError('Must supply a valid hostname')

    @property
    def _gateway_sal(self):
        data = self.data.copy()
        gw = self.node_sal.primitives.from_dict('gateway', data)
        gw.name = self.data["name"]
        return gw

    def install(self):
        print(colored('Install gateway {}'.format(self.data["name"]), 'white'))
        gateway_sal = self.gw_sal or self._gateway_sal
        gateway_sal.deploy()
        self.data['ztIdentity'] = gateway_sal.zt_identity

    def destroy(self, gateway_name=None):
        gateway_name = gateway_name or self.data["name"] 
        self.node_sal.primitives.drop_gateway(gateway_name)

    def stop(self):
        print(colored('Stop gateway {}'.format(self.data["name"]), 'white'))
        self._gateway_sal.stop()

    def start(self):
        print(colored('Start gateway {}'.format(self.data["name"]), 'white'))
        self.install()

    def generate_gw_sal(self):
        self.gw_sal = self._gateway_sal

    def add_network(self, name, type_, networkid=None):
        return self.gw_sal.networks.add(name=name, type_=type_, networkid=networkid)

    def add_zerotier(self, network, name=None):
        return self.gw_sal.networks.add_zerotier(network=network, name=None)

    def remove_network(self, item):
        self.gw_sal.networks.remove(item=item)

    def list_network(self):
        return self.gw_sal.networks.list()    

    def add_port_forward(self, name, source, target, protocols=None):
        self.gw_sal.portforwards.add(name=name, source=source, target=target, protocols=protocols)

    def remove_port_forward(self, item):
        self.gw_sal.portforwards.remove(item=item)