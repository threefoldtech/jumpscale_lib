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

    def _compare_objects(self, obj1, obj2, *keys):
        """
        Checks that obj1 and obj2 have different names, and that the combination of values from keys are unique
        :param obj1: first dict to use for comparison
        :param obj2: second dict to use for comparison
        :param keys: keys to use for value comparison
        :return: a tuple of bool, where the first element indicates whether the name matches or not,
        and the second element indicates whether the combination of values matches or not
        """
        name = obj1['name'] == obj2['name']
        for key in keys:
            if obj1[key] != obj2[key]:
                return name, False
        return name, True

    def add_http_proxy(self, proxy):
        print(colored('Add http proxy {}'.format(proxy['name']),'white'))

        for existing_proxy in self.data['httpproxies']:
            name, combination = self._compare_objects(existing_proxy, proxy, 'host')
            if name:
                raise ValueError('A proxy with the same name exists')
            if combination:
                raise ValueError("Proxy with host {} already exists".format(proxy['host']))
        self.data['httpproxies'].append(proxy)

        try:
            self._gateway_sal.configure_http()
        except:
            print(colored('Failed to add http proxy, restoring gateway to previous state', 'red'))
            self.data['httpproxies'].remove(proxy)
            self._gateway_sal.configure_http()
            raise

    def remove_http_proxy(self, name):
        print(colored('Remove http proxy {}'.format(name), 'white'))
        for existing_proxy in self.data['httpproxies']:
            if existing_proxy['name'] == name:
                self.data['httpproxies'].remove(existing_proxy)
                break
        else:
            return
        try:
            self._gateway_sal.configure_http()
        except:
            print(colored('Failed to remove http proxy, restoring gateway to previous state','red'))
            self.data['httpproxies'].append(existing_proxy)
            self._gateway_sal.configure_http()
            raise

    def add_dhcp_host(self, network_name, host):
        print(colored('Add dhcp to network {}'.format(network_name), 'white'))
        for network in self.data['networks']:
            if network['name'] == network_name:
                break
        else:
            raise LookupError('Network with name {} doesn\'t exist'.format(network_name))
        dhcpserver = network['dhcpserver']
        for existing_host in dhcpserver['hosts']:
            if existing_host['macaddress'] == host['macaddress']:
                raise ValueError('Host with macaddress {} already exists'.format(host['macaddress']))
        dhcpserver['hosts'].append(host)

        try:
            self._gateway_sal.configure_dhcp()
            self._gateway_sal.configure_cloudinit()
        except:
            print(colored('Failed to add dhcp host, restoring gateway to previous state','red'))
            dhcpserver['hosts'].remove(host)
            self._gateway_sal.configure_dhcp()
            self._gateway_sal.configure_cloudinit()
            raise

    def remove_dhcp_host(self, network_name, host):
        print('Add dhcp to network {}'.format(network_name), 'white')
        for network in self.data['networks']:
            if network['name'] == network_name:
                break
        else:
            raise LookupError('Network with name {} doesn\'t exist'.format(network_name))
        dhcpserver = network['dhcpserver']
        for existing_host in dhcpserver['hosts']:
            if existing_host['macaddress'] == host['macaddress']:
                dhcpserver['hosts'].remove(existing_host)
                break
        else:
            raise LookupError('Host with macaddress {} doesn\'t exist'.format(host['macaddress']))

        try:
            self._gateway_sal.configure_dhcp()
            self._gateway_sal.configure_cloudinit()
        except:
            print(colored('Failed to remove dhcp, restoring gateway to previous state','red'))
            dhcpserver['hosts'].append(existing_host)
            self._gateway_sal.configure_dhcp()
            self._gateway_sal.configure_cloudinit()
            raise

            
    def info(self):
        data = self._gateway_sal.to_dict(live=True)
        return {
            'name': self.data["name"],
            'portforwards': data['portforwards'],
            'httpproxies': data['httpproxies'],
            'networks': data['networks']
        }

    # def uninstall(self):
    #     print(colored('Uninstall gateway {}'.format(self.data["name"]), 'white'))
    #     self._gateway_sal.stop()

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