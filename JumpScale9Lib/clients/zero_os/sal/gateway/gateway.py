from js9 import j
from .http import HTTPServer
from .dhcp import DHCP
from .firewall import Firewall, Network
from .cloudinit import CloudInit
from zerotier import client
import ipaddress
import json
import yaml
import time

class Gateway:
    def __init__(self, container, data):
        self.container = container
        self.data = data
        self.validate_input(data)
        self.dhcpservers = []
        self.publicnetwork = None
        self.privatenetworks = []
        self.cloudinit_config = {}

        for nic in self.data['nics']:
            if nic.get("config"):
                if nic["config"].get("gateway", None):
                    self.publicnetwork = Network(nic["name"], nic["config"]["cidr"])
                else:
                    self.privatenetworks.append(Network(nic["name"], nic["config"]["cidr"]))
            dhcpserver = nic.get('dhcpserver')
            if not dhcpserver:
                continue
            cidr = ipaddress.IPv4Interface(nic['config']['cidr'])
            dhcpserver['subnet'] = str(cidr.network.network_address)
            dhcpserver['gateway'] = str(cidr.ip)
            dhcpserver['interface'] = nic['name']
            self.dhcpservers.append(dhcpserver)


            for host in dhcpserver.get("hosts", []):
                if host.get("cloudinit"):
                    if host["cloudinit"]["userdata"] and host["cloudinit"]["metadata"]:
                        userdata = yaml.load(host["cloudinit"]["userdata"])
                        metadata = yaml.load(host["cloudinit"]["metadata"])
                        self.cloudinit_config[host['macaddress'].lower()] = json.dumps({
                            "meta-data": metadata,
                            "user-data": userdata,
                        })


    @staticmethod
    def validate_input(data):
        domain = data.get('domain')
        if not domain:
            raise j.exceptions.Input('Domain cannot be empty.')

        nics = data.get('nics', [])
        for nic in nics:
            config = nic.get('config', {})
            name = nic.get('name')
            if not name:
                raise j.exceptions.Input('Gateway nic should have name defined.')
            if name[0].isnumeric():
                raise j.exceptions.Input("Bad nic definition '{name}', name shouldn't start with a number".format(name=name))
            dhcp = nic.get('dhcpserver')
            zerotierbridge = nic.get('zerotierbridge')
            cidr = config.get('cidr')

            if zerotierbridge and not zerotierbridge.get('id'):
                raise j.exceptions.Input('Zerotierbridge id not specified')

            if config:
                if config.get('gateway'):
                    if dhcp:
                        raise j.exceptions.Input('DHCP can only be defined for private networks')
            if dhcp:
                if not cidr:
                    raise j.exceptions.Input('Gateway nic should have cidr if a DHCP server is defined.')
                nameservers = dhcp.get('nameservers')

                if not nameservers:
                    raise j.exceptions.Input('DHCP nameservers should have at least one nameserver.')
                hosts = dhcp.get('hosts', [])
                subnet = ipaddress.IPv4Interface(cidr).network
                for host in hosts:
                    ip = host.get('ipaddress')
                    if not ip or not ipaddress.ip_address(ip) in subnet:
                        raise j.exceptions.Input('DHCP host ipaddress should be within cidr subnet.')


    def install(self):
        if not self.container.is_running():
            self.container.start()
        self.container.upload_content('/etc/resolv.conf', 'nameserver 127.0.0.1\n')
        self.setup_zerotierbridges()

        # setup cloud-init magical ip
        ip = self.container.client.ip
        loaddresses = ip.addr.list('lo')
        magicip = '169.254.169.254/32'
        if magicip not in loaddresses:
            ip.addr.add('lo', magicip)

        self.restore_certificates()
        self.configure_http()
        self.configure_fw()
        self.configure_dhcp()
        self.configure_cloudinit()
        self.save_certificates()

    def configure_dhcp(self):
        dhcp = DHCP(self.container, self.data['domain'], self.dhcpservers)
        dhcp.apply_config()

    def configure_cloudinit(self):
        cloudinit = CloudInit(self.container, self.cloudinit_config)
        cloudinit.apply_config()

    def configure_http(self):
        servers = {'http': [], 'https': []}
        for proxy in self.data['httpproxies']:
            if 'http' in proxy['types']:
                servers['http'].append(proxy)
            if 'https' in proxy['types']:
                servers['https'].append(proxy)
        for http_type, proxies in servers.items():
            if proxies:
                httpserver = HTTPServer(self.container, proxies, http_type)
                httpserver.apply_rules()

    def configure_fw(self):
        portforwards = self.data.get('portforwards', [])
        firewall = Firewall(self.container, self.publicnetwork, self.privatenetworks, portforwards)
        firewall.apply_rules()

    def save_certificates(self, caddy_dir="/.caddy"):
        if self.container.client.filesystem.exists(caddy_dir):
            certificates = []
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
                            certificates.append({"path": cert_path, "key": key, "metadata": metadata})

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
                            certificates.append({
                                "path": cert_path,
                                "key": key,
                                "metadata": metadata,
                                "cert": cert
                            })
            self.data['certificates'] = certificates

    def restore_certificates(self):
        certs = self.data.get('certificates', [])
        for cert in certs:
            self.container.client.filesystem.mkdir(cert['path'])
            self.container.upload_content("{}/{}.json".format(cert['path'], cert['path'].split('/')[-1]), cert['metadata'])
            self.container.upload_content("{}/{}.key".format(cert['path'], cert['path'].split('/')[-1]), cert['key'])
            if cert.get('cert'):
                self.container.upload_content("{}/{}.crt".format(cert['path'], cert['path'].split('/')[-1]), cert['cert'])

    def get_zerotier_nic(self, zerotierid):
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

    def setup_zerotierbridges(self):
        nics = self.data['nics']
        def wait_for_interface():
            start = time.time()
            while start + 60 > time.time():
                for link in self.container.client.ip.link.list():
                    if link['type'] == 'tun':
                        return
                time.sleep(0.5)
            raise j.exceptions.RuntimeError("Could not find zerotier network interface")

        ip = self.container.client.ip
        for nic in nics:
            zerotierbridge = nic.pop('zerotierbridge', None)
            if zerotierbridge:
                nicname = nic['name']
                linkname = 'l-{}'.format(nicname)[:15]
                wait_for_interface()
                zerotiername = self.get_zerotier_nic(zerotierbridge['id'])
                token = zerotierbridge.get('token')
                if token:
                    zerotier = client.Client()
                    zerotier.set_auth_header('bearer {}'.format(token))

                    resp = zerotier.network.getMember(self.container.model.data.zerotiernodeid, zerotierbridge['id'])
                    member = resp.json()

                    self.logger.info("Enable bridge in member {} on network {}".format(member['nodeId'], zerotierbridge['id']))
                    member['config']['activeBridge'] = True
                    zerotier.network.updateMember(member, member['nodeId'], zerotierbridge['id'])

                # check if configuration is already done
                linkmap = {link['name']: link for link in ip.link.list()}

                if linkmap[nicname]['type'] == 'bridge':
                    continue

                # bring related interfaces down
                ip.link.down(nicname)
                ip.link.down(zerotiername)

                # remove IP and rename
                ipaddresses = ip.addr.list(nicname)
                for ipaddr in ipaddresses:
                    ip.addr.delete(nicname, ipaddr)
                ip.link.name(nicname, linkname)

                # create bridge and add interface and IP
                ip.bridge.add(nicname)
                ip.bridge.addif(nicname, linkname)
                ip.bridge.addif(nicname, zerotiername)

                # readd IP and bring interfaces up
                for ipaddr in ipaddresses:
                    ip.addr.add(nicname, ipaddr)
                ip.link.up(nicname)
                ip.link.up(linkname)
                ip.link.up(zerotiername)

