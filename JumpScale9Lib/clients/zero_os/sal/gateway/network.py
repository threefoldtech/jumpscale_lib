from JumpScale9Lib.clients.zerotier.ZerotierClient import ZerotierClient, ZeroTierNetwork
from ..abstracts import Collection, Nic, ZTNic
from ..VM import VM
import netaddr

BASEMAC = netaddr.EUI('52:54:00:00:00:00')
BASEMAC.dialect = netaddr.mac_unix_expanded


class Users(Collection):
    def add(self, name, password, sudo=True, shell='/bin/bash', ssh_authorized_keys=None, **kwargs):
        """
        Add a user entry in the userdata of the cloudinit

        :param name: Username to configure on the node
        :type name: str
        :param password: Password to set for the user
        :type password: str
        :param sudo: Wether to allow the user to use sudo
        :type sudo: bool
        :param shell: Default shell to use for the user
        :type shell: str
        :param ssh_authorized_keys: List of public ssh keys to preauthorize for the user
        :type ssh_authorized_keys: list(str)
        :param kwargs: Extra settings to configure in userdata of the user
        :type kwargs: dict
        """
        user = {
            'name': name, 
            'shell': shell, 
            'lock-passwd': False, 
            'plain_text_passwd': password,
        }
        if sudo:
            user['sudo'] = 'ALL=(ALL) ALL'
        if ssh_authorized_keys:
            user['ssh_authorized_keys'] = ssh_authorized_keys
        user.update(kwargs)
        self._items.append(user)


class CloudInitStruct:
    def __init__(self, hostname):
        """
        Struct containing CloudInit data

        :param hostname: Hostname to configure on the node
        :type hostname: str
        """
        self._userdata = {
            'users': [], 
            'ssh_pwauth': True, 
            'manage_etc_hosts': True,
            'chpasswd': {'expire': False}
        }
        self.users = Users(None)
        self.metadata = {'local-hostname': hostname}

    @property
    def userdata(self):
        self._userdata['users'] = self.users.list()
        return self._userdata

    @userdata.setter
    def userdata(self, value):
        users = value.setdefault('users', [])
        users[:] = self.users.list()
        self._userdata = value


class Host:
    def __init__(self, name, macaddress, ipaddress):
        """
        DHCP Host entry

        :param name: Name of the host (hostname)
        :type name: str
        :param macaddress: Macaddress of the host
        :type macaddress: str
        :param ipaddress: IPAddress of the host
        :type ipaddress: str
        """
        self.name = name
        self.macaddress = macaddress
        self.ipaddress = ipaddress
        self.cloudinit = CloudInitStruct(name)

    def __str__(self):
        return "Host <{}: {}>".format(self.name, self.ipaddress)

    __repr__ = __str__

class Hosts(Collection):
    def __init__(self, gateway, network):
        super().__init__(gateway)
        self.network = network
        self.nameservers = ['8.8.8.8']

    def add(self, host, ipaddress, macaddress=None):
        """
        Add DHCP Host entry

        :param host: Name of the host (hostname) or VM object
        :type host: str or VM object
        :param ipaddress: IPAddress of the host
        :type ipaddress: str
        :param macaddress: Macaddress of the host
        :type macaddress: str
        """
        if not self.network.ip.cidr:
            raise ValueError('Can not configure hosts if network cidr is not set')
        if ipaddress not in self.network.ip.cidr:
            raise ValueError('IPAddresss {} is not in {}'.format(ipaddress, self.network.ip.cidr.cidr))
        if ipaddress == str(self.network.ip.cidr.ip):
            raise ValueError('IPAddresss {} can not be the same as the gateway.'.format(ipaddress))

        for configuredhost in self:
            if configuredhost.ipaddress == ipaddress:
                raise ValueError('IPAddress already in use by {}'.format(configuredhost.name))
            if macaddress and macaddress == configuredhost.macaddress:
                raise ValueError('MACAddress already in use by {}'.format(configuredhost.name))

        macaddress = macaddress or self.get_free_mac()
        if isinstance(host, VM):
            super().add(host.name)
            vm = host
            host = Host(vm.name, macaddress, ipaddress)
            vm.nics.add('nic_{}'.format(self.network.name), self.network.type, self.network.networkid, macaddress)
        else:
            super().add(host)
            host = Host(host, macaddress, ipaddress)
        self._items.append(host)
        return host

    def get_free_mac(self):
        usedmacs = [netaddr.EUI(host.macaddress).value for host in self]
        counter = 0
        while True:
            if BASEMAC.value + counter not in usedmacs:
                mac = netaddr.EUI(BASEMAC.value + counter)
                mac.dialect = netaddr.mac_unix_expanded
                return str(mac)
            counter += 1


class IP:
    def __init__(self, cidr=None, gateway=None):
        """
        IP Address configuration for network

        :param cidr: IPAdddress in cidr notation example: 192.168.58.1/24
        :type cidr: str
        :param gateway: Gateway to use for this network settings this will mark thet network as public
        :type gateway: str
        """
        if cidr:
            self._cidr = netaddr.IPNetwork(cidr)
        else:
            self._cidr = None
        self.gateway = gateway

    @property
    def cidr(self):
        return self._cidr

    @property
    def address(self):
        if self._cidr:
            return str(self._cidr.ip)
        return None

    @property
    def subnet(self):
        if self._cidr:
            return str(self._cidr.cidr)
        return None

    @property
    def netmask(self):
        if self._cidr:
            return str(self._cidr.netmask)
        return None

    @cidr.setter
    def cidr(self, value):
        self._cidr = netaddr.IPNetwork(value)

    def __str__(self):
        return "IP <{}>".format(self._cidr)

    __repr__ = __str__


class Networks(Collection):
    """
    Collection of networks beloning to the gateway
    """
    def add(self, name, type_, networkid=None):
        """
        Add network to the gateway

        :param name: Name of the network will also be used as interface name
                     Should not contain special characters and should not be
                     longer then 15 characters
        :type name: str
        :param type_: Type of network to add, choose between
                      vxlan, vlan, bridge, default or zerotier
        :type type_: str
        :param networkid: Depending on the networktype this can be vlantag, vxlan id or zerotier network id
        :type networkid: mixed(str, int)
        """
        super().add(name)
        if len(name) > 15 or name == 'default':
            raise ValueError('Invalid network name {} should be max 15 chars and not be \'default\''.format(name))
        if networkid is None and type_ != 'default':
            raise ValueError('Missing required argument networkid for type {}'.format(type_))
        if type_ not in ['vxlan', 'zerotier', 'vlan', 'bridge', 'default']:
            raise ValueError('Invalid network type: {}'.format(type_))
        if type_ == 'vxlan':
            network = VXlanNetwork(name, networkid, self._parent)
        elif type_ == 'vlan':
            network = VlanNetwork(name, networkid, self._parent)
        elif type_ == 'zerotier':
            network = ZTNetwork(name, networkid, self._parent)
        else:
            network = Network(name, networkid, type_, self._parent)
        self._items.append(network)
        return network

    def add_zerotier(self, network, name=None):
        """
        Add zerotier by zerotier network


        When adding a zerotier network based on the ZerotierClient a new ZerotierNework will be created unless
        the networkid attribute is set.

        :param network: Zerotier network instance or Zerotier client(part of zerotierclient)
        :type network: JumpScale9Lib.clients.zerotier.ZerotierClient.ZeroTierNetwork or JumpScale9Lib.clients.zerotier.ZerotierClient.ZerotierClient
        :param name: Name for the nic if left blank will be the name of the network
        :type name: str
        """
        if isinstance(network, ZeroTierNetwork):
            name = name or network.name
            net = ZTNetwork(name, network.id, self._parent)
            net.client = network.client
        elif isinstance(network, ZerotierClient):
            if not name:
                raise ValueError('Need to provide a name for network')
            net = ZTNetwork(name, None, self._parent)
            net.client = network
        else:
            raise ValueError('Unsupported value password for network')
        self._items.append(net)
        return net


class Network(Nic):
    def __init__(self, name, networkid, type_, gateway):
        """
        Abstract Network implementation

        :param name: Name of the network will also be used as interface name
                     Should not contain special characters and should not be
                     longer then 12 characters
        :type name: str
        :type type_: str
        :param gateway: Gateway instance 
        :type gateway: Gateway
        """
        super().__init__(name, type_, networkid, None, gateway)
        self.ip = IP()
        self.hosts = Hosts(gateway, self)

    def __str__(self):
        return "{} <{} {}>".format(self.__class__.__name__, self.name, self.type)

    def to_dict(self, forcontainer=False):
        data = super().to_dict(forcontainer=forcontainer)
        if self.ip.cidr:
            data['config'] = {'cidr': str(self.ip.cidr), 'gateway': self.ip.gateway}
        return data

    __repr__ = __str__


class VlanNetwork(Network):
    """
    VLAN specific Network implementation
    """
    def __init__(self, name, networkid, gateway):
        self._networkid = None
        super().__init__(name, networkid, 'vlan', gateway)

    @property
    def networkid(self):
        return str(self._networkid)

    @networkid.setter
    def networkid(self, value):
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
            else:
                raise ValueError('Invalid value for vlantag')
        if not isinstance(value, int) or (value < 0 or value > 4096):
            raise ValueError('Invalid value for vlantag')
        self._networkid = value

    @property
    def vlantag(self):
        return self.networkid

    @vlantag.setter
    def vlantag(self, value):
        self.networkid = value


class VXlanNetwork(Network):
    """
    VXLAN specific Network implementation
    """
    def __init__(self, name, networkid, gateway):
        self._networkid = None
        super().__init__(name, networkid, 'vxlan', gateway)

    @property
    def networkid(self):
        return str(self._networkid)

    @networkid.setter
    def networkid(self, value):
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
            else:
                raise ValueError('Invalid value for vxlan id')
        if not isinstance(value, int) or value < 0:
            raise ValueError('Invalid value for vxlan id')
        self._networkid = value

    @property
    def vxlan(self):
        return self.networkid

    @vxlan.setter
    def vxlan(self, value):
        self.networkid = value



class ZTNetwork(ZTNic):
    """
    Zerotier specific Network implementation
    """
    def __init__(self, name, networkid, gateway):
        self._networkid = None
        super().__init__(name, networkid, None, gateway)
        self.ip = IP()
        self.hosts = Hosts(gateway, self)
        self.client = None

    @property
    def networkid(self):
        return str(self._networkid)

    @networkid.setter
    def networkid(self, value):
        if not isinstance(value, str) or len(value) != 16:
            raise ValueError('Invalid value for zerotierid')
        self._networkid = value

