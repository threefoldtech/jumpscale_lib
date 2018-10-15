import netaddr
from jumpscale import j
import time

OVS_FLIST = 'https://hub.grid.tf/tf-official-apps/ovs.flist'


def combine(ip1, ip2, mask):
    """
    >>> combine('10.0.3.11', '192.168.1.10', 24)
    '10.0.3.10'
    """
    iip1 = netaddr.IPNetwork('{}/{}'.format(ip1, mask))
    iip2 = netaddr.IPNetwork('{}/{}'.format(ip2, mask))
    ires = iip1.network + int(iip2.ip & (~ int(iip2.netmask)))
    net = netaddr.IPNetwork(ires)
    net.prefixlen = mask
    return net


class Network():

    def __init__(self, node):
        self.node = node

    @property
    def client(self):
        return self.node.client

    def get_management_info(self):

        def get_nic_ip(nics, name):
            for nic in nics:
                if nic['name'] == name:
                    for ip in nic['addrs']:
                        return netaddr.IPNetwork(ip['addr'])
                    return

        defaultgwdev = self.client.bash("ip route | grep default | awk '{print $5}'").get().stdout.strip()
        nics = self.client.info.nic()
        mgmtaddr = None
        if defaultgwdev:
            ipgwdev = get_nic_ip(nics, defaultgwdev)
            if ipgwdev:
                mgmtaddr = str(ipgwdev.ip)
        if not mgmtaddr:
            mgmtaddr = self.node.addr

        return mgmtaddr

    def _ensure_ovs_container(self, name):
        try:
            container = self.node.containers.get(name)
        except LookupError:
            container = self.node.containers.create(name, OVS_FLIST, 'ovs', host_network=True, privileged=True)
        return container

    def get_addresses(self, network):
        mgmtaddr = self.get_management_info()
        return {
            'storageaddr': combine(str(network.ip), mgmtaddr, network.prefixlen),
            'vxaddr': combine('10.240.0.0', mgmtaddr, network.prefixlen),
        }

    def get_free_nics(self):
        devices = []
        for device in self.client.ip.link.list():
            if device['type'] == 'device':
                if device['up'] == False:
                    self.client.ip.link.up(device['name'])
                devices.append(device['name'])
        nics = list(filter(lambda nic: nic['name'] in devices, self.client.info.nic()))
        nics.sort(key=lambda nic: nic['speed'])
        availablenics = {}
        for nic in nics:
            # skip all interface that have an ipv4 address
            if any(netaddr.IPNetwork(addr['addr']).version == 4 for addr in nic['addrs'] if 'addr' in addr):
                continue
            if nic['speed'] == 0:
                continue
            availablenics.setdefault(nic['speed'], []).append(nic['name'])
        return sorted(availablenics.items(), reverse=True)

    def reload_driver(self, driver):
        self.node.client.system('modprobe -r {}'.format(driver)).get()
        devs = {link['name'] for link in self.node.client.ip.link.list()}
        self.node.client.system('modprobe {}'.format(driver)).get()
        # brings linsk up
        alldevs = {link['name'] for link in self.node.client.ip.link.list()}
        driverdevs = alldevs - devs
        for link in driverdevs:
            self.node.client.ip.link.up(link)

        # wait max 10 seconds for these nics to become up (speed available)
        now = time.time()
        while time.time() - 10 < now:
            for nic in self.node.client.info.nic():
                if nic['speed'] and nic['name'] in driverdevs:
                    driverdevs.remove(nic['name'])
            if not driverdevs:
                break
            time.sleep(1)

    def configure(self, cidr, vlan_tag, ovs_container_name,  bonded=False):
        container = self._ensure_ovs_container(ovs_container_name)
        if not container.is_running():
            container.start()

        nicmap = {nic['name']: nic for nic in self.node.client.info.nic()}
        # freenics = ([1000, ['eth0']], [100, ['eth1']])
        freenics = self.node.network.get_free_nics()
        if not freenics:
            raise j.exceptions.RuntimeError("Could not find available nic")

        network = netaddr.IPNetwork(cidr)
        addresses = self.get_addresses(network)

        interfaces = None
        if not bonded:
            interfaces = [freenics[0][1][0]]
        else:
            for speed, interfaces in freenics:
                if len(interfaces) >= 2:
                    interfaces = interfaces[:2]
                    break
            else:
                raise j.exceptions.RuntimeError("Could not find two equal available nics")

        if 'backplane' not in nicmap:
            container.client.json('ovs.bridge-add', {"bridge": "backplane"})
            if not bonded:
                container.client.json('ovs.port-add', {"bridge": "backplane", "port": interfaces[0], "vlan": 0})
            else:
                container.client.json('ovs.bond-add', {"bridge": "backplane",
                                                       "port": "bond0",
                                                       "links": interfaces,
                                                       "lacp": False,
                                                       "mode": "balance-slb"})
                                                       
            for interface in interfaces:
                self.node.client.ip.link.mtu(interface, 2000)
                self.node.client.ip.link.up(interface)
            self.node.client.ip.link.up('backplane')
            self.node.client.ip.addr.add('backplane', str(addresses['storageaddr']))