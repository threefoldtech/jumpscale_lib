from jumpscale import j
import copy
from termcolor import colored


class GW:

    def __init__(self, node, guid=None, data=None):
        self.data = data
        self.node_sal = node
        self.guid= guid

    def validate(self):
        if not self.data['hostname']:
            raise ValueError('Must supply a valid hostname')

    @property
    def _gateway_sal(self):
        data = self.data.copy()
        gw = self.node_sal.primitives.from_dict('gateway', data)
        gw.name = self.guid
        return gw

    def install(self, gateway_sal=None):
        print(colored('Install gateway {}'.format(self.data["name"]), 'white'))
        gateway_sal = gateway_sal or self._gateway_sal
        gateway_sal.deploy()
        self.data['ztIdentity'] = gateway_sal.zt_identity

    def destroy(self, gateway_name=None):
        gateway_name = gateway_name or self.data["name"] 
        self.node_sal.drop_gateway(gateway_name)

    def add_portforward(self, forward):
        print(colored('Add portforward {}'.format(forward['name']), 'white'))
        for network in self.data['networks']:
            if network['name'] == forward['srcnetwork']:
                break
        else:
            raise LookupError('Network with name {} doesn\'t exist'.format(forward['srcnetwork']))

        for fw in self.data['portforwards']:
            name, combination = self._compare_objects(fw, forward, 'srcnetwork', 'srcport')
            if name:
                raise ValueError('A forward with the same name exists')
            if combination:
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    raise ValueError('Forward conflicts with existing forward')
        self.data['portforwards'].append(forward)

        try:
            self._gateway_sal.configure_fw()
        except:
            print(colored('Failed to add portforward, restoring gateway to previous state','red'))
            self.data['portforwards'].remove(forward)
            self._gateway_sal.configure_fw()
            raise

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

    def remove_portforward(self, name):
        print(colored('Remove portforward {}'.format(name), 'white'))

        for fw in self.data['portforwards']:
            if fw['name'] == name:
                self.data['portforwards'].remove(fw)
                break
        else:
            return

        try:
            self._gateway_sal.configure_fw()
        except:
            print(colored('Failed to remove portforward, restoring gateway to previous state', 'red'))
            self.data['portforwards'].append(fw)
            self._gateway_sal.configure_fw()
            raise

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

    def add_network(self, network):
        print('Add network {}'.format(network['name']), 'white')

        for existing_network in self.data['networks']:
            name, combination = self._compare_objects(existing_network, network, 'type', 'id')
            if name:
                raise ValueError('Network with name {} already exists'.format(name))
            if combination:
                raise ValueError('network with same type/id combination already exists')
        self.data['networks'].append(network)

        try:
            self._gateway_sal.deploy()
        except:
            print(colored('Failed to add network, restoring gateway to previous state','red'))
            self.data['networks'].remove(network)
            self._gateway_sal.deploy()
            raise

    def remove_network(self, name):
        print(colored('Remove network {}'.format(name), 'white'))

        for network in self.data['networks']:
            if network['name'] == name:
                self.data['networks'].remove(network)
                break
        else:
            return
        try:
            self._gateway_sal.deploy()
        except:
            print(colored('Failed to remove network, restoring gateway to previous state','red'))
            self.data['networks'].append(network)
            self._gateway_sal.deploy()
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
