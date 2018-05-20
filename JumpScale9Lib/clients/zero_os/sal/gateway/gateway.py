from js9 import j
from .http import HTTPServer
from .dhcp import DHCP
from .firewall import Firewall
from ..abstracts import Collection
from .network import Networks
from .cloudinit import CloudInit
import yaml
import time


class DestBind:
    def __init__(self, ipaddress, port):
        """
        Portforward target bind instance
        :param ipaddress: ip to forward to
        :type ipaddress: str
        :param port: port to forward to
        :type port: int
        """
        self.ipaddress = ipaddress
        self.port = port

    def __str__(self):
        return "Bind <{}:{}>".format(self.ipaddress, self.port)

    __repr__ = __str__


class SourceBind:
    def __init__(self, parent, network_name, port):
        """
        Portforward source bind instance

        :param parent: the parent of the forward
        :type parent: Gateway
        :param network_name: the network name to get the source ip from
        :type network_name: str
        :param port: the source port to forward from
        :type port
        """
        self.network_name = network_name
        self.port = port
        self.parent = parent

    @property
    def ipaddress(self):
        return self.parent.networks[self.network_name].ip.address

    @ipaddress.setter
    def ipaddress(self):
        raise RuntimeError('ipaddress can\'t be set')

    def __str__(self):
        return "Source Bind <{}:{}>".format(self.network_name, self.port)

    __repr__ = __str__


class Forward:
    def __init__(self, parent, name, source=None, target=None, protocols=None):
        """
        Initialize forward

        :param parent: the parent of the forward
        :type parent: Gateway
        :param name: Logical name to give to the portforward
        :type name: str
        :param source: Source Network/Port for the portforwards
        :type source: tuple(str, int) or instance of SourceBind
        :param target: Target IP/Port for the portforwards
        :type target: tuple(str, int) or instance of DestBind
        :param protocols: Protocols to forward tcp or udp
        :type protocols: list(str)
        """
        self.name = name
        if protocols:
            for protocol in protocols:
                if protocol not in ['tcp', 'udp']:
                    raise ValueError('Invalid protocol {} for portforward'.format(protocol))
        if protocols is None:
            protocols = ['tcp']
        self.protocols = protocols
        if isinstance(source, tuple):
            self.source = SourceBind(parent, *source)
        elif isinstance(source, SourceBind):
            self.source = source
        if self.source.network_name not in parent.networks:
            raise LookupError('Network with name {} doesn\'t exist'.format(self.source.network_name))

        if isinstance(target, tuple):
            self.target = DestBind(*target)
        elif isinstance(target, DestBind):
            self.target = target

    def __str__(self):
        return "Forward <{}:{}>".format(self.source, self.target)

    __repr__ = __str__


class PortForwards(Collection):
    def add(self, name, source, target, protocols=None):
        """
        Add portforward to the gateway

        :param name: Logical name to give to the portforward
        :type name: str
        :param source: Source Network/Port for the portforwards
        :type source: tuple(str, int) or instance of SourceBind
        :param target: Target IP/Port for the portforwards
        :type target: tuple(str, int) or instance of DestBind
        :param protocols: Protocols to forward tcp or udp
        :type protocols: list(str)
        """
        super().add(name)
        forward = Forward(self._parent, name, source, target, protocols)
        self._items.append(forward)
        return forward


class HTTPProxy:
    def __init__(self, name, host, destinations, types=None):
        """
         Httproxy instance
        :param name: logical name of the http proxy
        :type name: str
        :param host: Host to forward for typical a dns like eg: example.org
        :type host: str
        :param destinations: One or more destination to forward to:
                                eg: ['http://192.168.103.2:8080']
        :type destinations: list(str)
        :param types: Type of proxy http or https
        :type types: list(str)
        """
        self.name = name
        self.host = host
        if types:
            for proxy_type in types:
                if proxy_type not in ['http', 'https']:
                    raise ValueError('Invalid type {} for http proxy'.format(proxy_type))
        if types is None:
            types = ['http', 'https']
        self.types = types
        self.destinations = destinations

    def __str__(self):
        return "Proxy <{}:{}>".format(self.host, self.destinations)

    __repr__ = __str__


class HTTPProxies(Collection):
    def add(self, name, host, destinations, types=None):
        """
        Add http proxy to the gateway
        :param name: logical name of the http proxy
        :type name: str
        :param host: Host to forward for typical a dns like eg: example.org
        :type host: str
        :param destinations: One or more destination to forward to:
                                eg: ['http://192.168.103.2:8080']
        :type destinations: list(str)
        :param types: Type of proxy http or https
        :type types: list(str)
        """
        super().add(name)
        proxy = HTTPProxy(name, host, destinations, types)
        self._items.append(proxy)
        return proxy


class Gateway:
    def __init__(self, node, name):
        """
        Gateway Sal
        :param node: node sal object
        :type node: class Node
        :param name: gateway logical name
        :type name: str
        """
        self.name = name
        self.node = node
        self.domain = 'lan'
        self._container = None
        self.networks = Networks(self)
        self.flist = 'https://hub.gig.tech/gig-official-apps/zero-os-gw-master.flist'
        self.portforwards = PortForwards(self)
        self.httpproxies = HTTPProxies(self)
        self.certificates = []
        self.zt_identity = None
        self._default_nic = ''  # the name of the default network if there is one

    def from_dict(self, data):
        """
        Initialize networks, portforwards, httpproxies and certificates from data.

        :param data: data to use for initialization
        :type data: dict following the schema of the gateway template https://github.com/zero-os/0-templates/tree/master/templates/gateway/schema.capnp
        """
        self.networks = Networks(self)
        self.portforwards = PortForwards(self)
        self.httpproxies = HTTPProxies(self)
        self.zt_identity = data.get('ztIdentity')
        self.domain = data.get('domain') or 'lan'
        self.certificates = data.get('certificates', [])
        for nic in data.get('networks', []):
            network = self.networks.add(nic['name'], nic['type'], nic.get('id'))
            if nic.get('config'):
                network.ip.gateway = nic['config'].get('gateway', None)
                network.ip.cidr = nic['config'].get('cidr', None)
            if network.type == 'zerotier':
                network.client_name = nic.get('ztClient')
            if network.type == 'default':
                self._default_nic = network.name
            if nic.get('hwaddr'):
                network.hwaddr = nic['hwaddr']
            dhcpserver = nic.get('dhcpserver')
            if not dhcpserver:
                continue
            network.hosts.nameservers = dhcpserver['nameservers']
            network.hosts.pool_size = dhcpserver.get('poolSize', network.hosts.pool_size)
            network.hosts.pool_start = dhcpserver.get('poolStart', network.hosts.pool_start)
            for host in dhcpserver['hosts']:
                dhcphost = network.hosts.add(host['hostname'], host['ipaddress'], host['macaddress'])
                if host['cloudinit']['userdata']:
                    dhcphost.cloudinit.userdata = yaml.load(host['cloudinit']['userdata'])
                if host['cloudinit']['metadata']:
                    dhcphost.cloudinit.metadata = yaml.load(host['cloudinit']['metadata'])
        for forward in data['portforwards']:
            self.portforwards.add(forward['name'],
                                  (forward['srcnetwork'], forward['srcport']),
                                  (forward['dstip'], forward['dstport']),
                                  forward['protocols'])
        for proxy in data['httpproxies']:
            self.httpproxies.add(proxy['name'], proxy['host'], proxy['destinations'], proxy['types'])

    def deploy(self):
        """
        Deploy gateway in reality
        """
        if not self._default_nic:
            publicnetworks = list(filter(lambda net: net.ip.gateway, self.networks))
            if len(publicnetworks) != 1:
                raise RuntimeError('Need exactly one network with a gateway')
        if self.container is None:
            self.create_container()
        elif not self.container.is_running():
            self.container.start()
        self.container.upload_content('/etc/resolv.conf', 'nameserver 127.0.0.1\n')
        self.setup_zerotier()

        # setup cloud-init magical ip
        ip = self.container.client.ip
        loaddresses = ip.addr.list('lo')
        magicip = '169.254.169.254/32'
        if magicip not in loaddresses:
            ip.addr.add('lo', magicip)
        if 'cloudinit' not in self.httpproxies:
            self.httpproxies.add('cloudinit', '169.254.169.254', ['http://127.0.0.1:8080'], ['http'])

        self.update_nics()
        self.restore_certificates()
        self.configure_http()
        self.configure_fw()
        self.configure_dhcp()
        self.configure_cloudinit()
        self.save_certificates()

    def stop(self):
        """
        Stop a gateway by stopping the container
        """
        if self.container:
            self.container.stop()

    def update_nics(self):
        """
        Apply gateway's networks to gateway container's nics
        """
        if self.container is None:
            raise RuntimeError('Can not update nics when gateway is not deployed')
        toremove = []
        wantednetworks = list(self.networks)
        for nic in self.container.nics:
            try:
                network = self.networks[nic['name']]
                wantednetworks.remove(network)
            except KeyError:
                toremove.append(nic)
        for removeme in toremove:
            if removeme['type'] == 'default':
                self._remove_container_portforwards()
            self.container.remove_nic(removeme['name'])

        for network in wantednetworks:
            self.container.add_nic(network.to_dict())
            if network.type == 'default':
                self._update_container_portforwards()

    def _container_name(self):
        """
        Return the name used for gateway's container
        :return: container name
        :rtype: str
        """
        return 'gw_{}'.format(self.name)

    @property
    def container(self):
        """
        Get container to run gateway services on

        :return: Container object or None
        :rtype: Container
        """
        if self._container is None:
            try:
                self._container = self.node.containers.get(self._container_name())
            except LookupError:
                return None
        return self._container

    def create_container(self):
        """
        Create the gateway container
        """
        nics = []
        if not self.zt_identity:
            self.zt_identity = self.node.client.system('zerotier-idtool generate').get().stdout.strip()
        ztpublic = self.node.client.system('zerotier-idtool getpublic {}'.format(self.zt_identity)).get().stdout.strip()

        for network in self.networks:
            if network.type == 'zerotier':
                if not network.networkid:
                    if not network.client:
                        raise RuntimeError('Zerotier network should either have client or networkid assigned')
                    cidr = network.ip.subnet or '172.20.0.0/16'
                    ztnetwork = network.client.network_create(False, cidr, name=network.name)
                    network.networkid = ztnetwork.id
                if network.client:
                    ztnetwork = network.client.network_get(network.networkid)
                    privateip = None
                    if network.ip.cidr:
                        privateip = str(network.ip.cidr)
                    ztnetwork.member_add(ztpublic, self.name, private_ip=privateip)
            nics.append(network.to_dict(forcontainer=True))
            # zerotierbridge = nic.pop('zerotierbridge', None)
            # if zerotierbridge:
            #    contnics.append(
            #        {
            #            'id': zerotierbridge['id'], 'type': 'zerotier',
            #            'name': 'z-{}'.format(nic['name']), 'token': zerotierbridge.get('token', '')
            #        })
        self._container = self.node.containers.create(self._container_name(), self.flist, hostname=self.name, nics=nics,
                                                      privileged=True, identity=self.zt_identity)
        return self._container

    def to_dict(self):
        """
        Convert the gateway object to a dict.
        :return: a dict representation of the gateway matching the schema of the gateway template
                 https://github.com/zero-os/0-templates/tree/master/templates/gateway/schema.capnp
        :rtype: dict
        """
        data = {
            'networks': [],
            'hostname': self.name,
            'portforwards': [],
            'httpproxies': [],
            'domain': self.domain,
            'certificates': self.certificates,
            'ztIdentity': self.zt_identity,
        }
        for network in self.networks:
            nic = network.to_dict()
            if network.hosts.list():
                hosts = []
                dhcp = {
                    'nameservers': network.hosts.nameservers,
                    'hosts': hosts,
                    'poolStart': network.hosts.pool_start,
                    'poolSize': network.hosts.pool_size,
                }
                for networkhost in network.hosts:
                    host = {
                        'macaddress': networkhost.macaddress,
                        'ipaddress': networkhost.ipaddress,
                        'hostname': networkhost.name,
                        'cloudinit': {
                            'userdata': yaml.dump(networkhost.cloudinit.userdata),
                            'metadata': yaml.dump(networkhost.cloudinit.userdata),
                        }
                    }
                    hosts.append(host)
                nic['dhcpserver'] = dhcp
            data['networks'].append(nic)
        for proxy in self.httpproxies:
            data['httpproxies'].append({
                'host': proxy.host,
                'destinations': proxy.destinations,
                'types': proxy.types,
                'name': proxy.name,
            })
        for forward in self.portforwards:
            data['portforwards'].append({
                'srcport': forward.source.port,
                'srcnetwork': forward.source.ipaddress,
                'dstport': forward.target.port,
                'dstip': forward.target.ipaddress,
                'protocols': forward.protocols,
                'name': forward.name,
            })
        return data

    def to_json(self):
        """
        Create a json string of the result of to_dict function
        """
        return j.data.serializer.json.dumps(self.to_dict())

    def configure_dhcp(self):
        """
        Configure dhcp server based on the hosts added to the networks
        """
        if self.container is None:
            raise RuntimeError('Can not configure dhcp when gateway is not deployed')
        dhcp = DHCP(self.container, self.domain, self.networks)
        dhcp.apply_config()

    def configure_cloudinit(self):
        """
        Configure cloudinit
        """
        if self.container is None:
            raise RuntimeError('Can not configure cloudinit when gateway is not deployed')
        cloudinit = CloudInit(self.container, self.networks)
        cloudinit.apply_config()

    def configure_http(self):
        """
        Configure http server based on the httpproxies
        """
        if self.container is None:
            raise RuntimeError('Can not configure http when gateway is not deployed')
        servers = {'http': [], 'https': []}
        for proxy in self.httpproxies:
            if 'http' in proxy.types:
                servers['http'].append(proxy)
            if 'https' in proxy.types:
                servers['https'].append(proxy)
        for http_type, proxies in sorted(servers.items(), reverse=True):
            if proxies:
                httpserver = HTTPServer(self.container, proxies, http_type)
                httpserver.apply_rules()

    def configure_fw(self):
        """
        Configure nftables based on the networks and portforwards
        """
        if self.container is None:
            raise RuntimeError('Can not configure fw when gateway is not deployed')

        if self._default_nic:
            self._update_container_portforwards()

        firewall = Firewall(self.container, self.networks, self.portforwards)
        firewall.apply_rules()

    def _remove_container_portforwards(self):
        """
        Remove all portforwards on the gateway container
        """
        for host_port, container_port in self.container.info['container']['arguments']['port'].items():
            self.container.node.client.container.remove_portforward(
                self.container.id, host_port, int(container_port))

    def _update_container_portforwards(self):
        """
        Update the gateway container portforwards
        """
        container_forwards = set([v for k, v in self.container.info['container']['arguments']['port'].items() if v == int(k)])
        wanted_forwards = {80, 443}
        container_ip = str(self.container.default_ip(self._default_nic).ip)
        for forward in self.portforwards:
            source = forward.source
            if str(source.ipaddress) == container_ip:
                wanted_forwards.add(source.port)
        for port in container_forwards - wanted_forwards:
            self.container.node.client.container.remove_portforward(self.container.id, port, port)
        for port in wanted_forwards - container_forwards:
            self.container.node.client.container.add_portforward(self.container.id, port, port)

    def save_certificates(self, caddy_dir="/.caddy"):
        """
        Store https certificates in self.certificates
        """
        if self.container.client.filesystem.exists(caddy_dir):
            self.certificates = []
            for cert_authority in self.container.client.filesystem.list("{}/acme/".format(caddy_dir)):
                if cert_authority['is_dir']:
                    users = []
                    sites = []
                    if self.container.client.filesystem.exists("{}/acme/{}/users".format(caddy_dir, cert_authority['name'])):
                        users = self.container.client.filesystem.list("{}/acme/{}/users".format(caddy_dir, cert_authority['name']))
                    if self.container.client.filesystem.exists("{}/acme/{}/sites".format(caddy_dir, cert_authority['name'])):
                        sites = self.container.client.filesystem.list("{}/acme/{}/sites".format(caddy_dir, cert_authority['name']))
                    for user in users:
                        if user['is_dir']:
                            cert_path = "{}/acme/{}/users/{}".format(caddy_dir, cert_authority['name'], user['name'])
                            metadata = key = cert = ""
                            if self.container.client.filesystem.exists("{}/{}.json".format(cert_path, user['name'])):
                                metadata = self.container.download_content("{}/{}.json".format(cert_path, user['name']))
                            if self.container.client.filesystem.exists("{}/{}.key".format(cert_path, user['name'])):
                                key = self.container.download_content("{}/{}.key".format(cert_path, user['name']))
                            self.certificates.append({"path": cert_path, "key": key, "metadata": metadata})

                    for site in sites:
                        if site['is_dir']:
                            cert_path = "{}/acme/{}/sites/{}".format(caddy_dir, cert_authority['name'], site['name'])
                            metadata = key = cert = ""
                            if self.container.client.filesystem.exists("{}/{}.json".format(cert_path, site['name'])):
                                metadata = self.container.download_content("{}/{}.json".format(cert_path, site['name']))
                            if self.container.client.filesystem.exists("{}/{}.key".format(cert_path, site['name'])):
                                key = self.container.download_content("{}/{}.key".format(cert_path, site['name']))
                            if self.container.client.filesystem.exists("{}/{}.crt".format(cert_path, site['name'])):
                                cert = self.container.download_content("{}/{}.crt".format(cert_path, site['name']))
                            self.certificates.append({
                                "path": cert_path,
                                "key": key,
                                "metadata": metadata,
                                "cert": cert
                            })

    def restore_certificates(self):
        """
        Restore https certifcates if loaded into self.certificates
        """
        for cert in self.certificates:
            self.container.client.filesystem.mkdir(cert['path'])
            self.container.upload_content("{}/{}.json".format(cert['path'], cert['path'].split('/')[-1]), cert['metadata'])
            self.container.upload_content("{}/{}.key".format(cert['path'], cert['path'].split('/')[-1]), cert['key'])
            if cert.get('cert'):
                self.container.upload_content("{}/{}.crt".format(cert['path'], cert['path'].split('/')[-1]), cert['cert'])

    def get_zerotier_nic(self, zerotierid):
        """
        Get the zerotier network device
        :param zerotierid: id of the zerotier
        :type zerotierid: str
        :return: zerotier network device name
        :rtype: str
        """
        for zt in self.container.client.zerotier.list():
            if zt['id'] == zerotierid:
                return zt['portDeviceName']
        else:
            raise j.exceptions.RuntimeError("Failed to get zerotier network device")

    def cleanup_zerotierbridge(self, nic):
        zerotierbridge = nic.pop('zerotierbridge', None)
        ip = self.container.client.ip
        if zerotierbridge:
            nicname = nic['name']
            linkname = 'l-{}'.format(nicname)[:15]
            zerotiername = self.get_zerotier_nic(zerotierbridge['id'])

            # bring related interfaces down
            ip.link.down(nicname)
            ip.link.down(linkname)
            ip.link.down(zerotiername)

            # remove IPs
            ipaddresses = ip.addr.list(nicname)
            for ipaddr in ipaddresses:
                ip.addr.delete(nicname, ipaddr)

            # delete interfaces/bridge
            ip.bridge.delif(nicname, zerotiername)
            ip.bridge.delif(nicname, linkname)
            ip.bridge.delete(nicname)

            # rename interface and readd IPs
            ip.link.name(linkname, nicname)
            for ipaddr in ipaddresses:
                ip.addr.add(nicname, ipaddr)

            # bring interfaces up
            ip.link.up(nicname)
            ip.link.up(zerotiername)

    def setup_zerotier(self):
        # TODO: Implement zerotierbridge
        def wait_for_interface():
            start = time.time()
            while start + 60 > time.time():
                for link in self.container.client.ip.link.list():
                    if link['type'] == 'tun':
                        return
                time.sleep(0.5)
            raise j.exceptions.RuntimeError("Could not find zerotier network interface")

        ip = self.container.client.ip
        for network in self.networks:
            continue
            # zerotierbridge = nic.pop('zerotierbridge', None)
            # if zerotierbridge:
            #     nicname = nic['name']
            #     linkname = 'l-{}'.format(nicname)[:15]
            #     wait_for_interface()
            #     zerotiername = self.get_zerotier_nic(zerotierbridge['id'])
            #     token = zerotierbridge.get('token')
            #     if token:
            #         zerotier = client.Client()
            #         zerotier.set_auth_header('bearer {}'.format(token))

            #         resp = zerotier.network.getMember(self.container.model.data.zerotiernodeid, zerotierbridge['id'])
            #         member = resp.json()

            #         self.logger.info("Enable bridge in member {} on network {}".format(member['nodeId'], zerotierbridge['id']))
            #         member['config']['activeBridge'] = True
            #         zerotier.network.updateMember(member, member['nodeId'], zerotierbridge['id'])

            #     # check if configuration is already done
            #     linkmap = {link['name']: link for link in ip.link.list()}

            #     if linkmap[nicname]['type'] == 'bridge':
            #         continue

            #     # bring related interfaces down
            #     ip.link.down(nicname)
            #     ip.link.down(zerotiername)

            #     # remove IP and rename
            #     ipaddresses = ip.addr.list(nicname)
            #     for ipaddr in ipaddresses:
            #         ip.addr.delete(nicname, ipaddr)
            #     ip.link.name(nicname, linkname)

            #     # create bridge and add interface and IP
            #     ip.bridge.add(nicname)
            #     ip.bridge.addif(nicname, linkname)
            #     ip.bridge.addif(nicname, zerotiername)

            #     # readd IP and bring interfaces up
            #     for ipaddr in ipaddresses:
            #         ip.addr.add(nicname, ipaddr)
            #     ip.link.up(nicname)
            #     ip.link.up(linkname)
            #     ip.link.up(zerotiername)
