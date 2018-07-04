import time

from js9 import j

from .Client import Client
from .sal.Minio import Minio, DEFAULT_PORT
from .sal.Node import Node
from .sal.Restic import Restic
from .sal.TfChain import TfChain
from .sal.ZeroRobot import ZeroRobot
from .sal.VM import VM
from .sal.Hypervisor import Hypervisor

from .sal.Mongodb import Mongodb
from .sal.Mongodb import Mongod
from .sal.Mongodb import Mongos

JSConfigFactoryBase = j.tools.configmanager.base_class_configs
logger = j.logger.get(__name__)


class ZeroOSFactory(JSConfigFactoryBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zos"
        super().__init__(Client)
        self.connections = {}
        self.sal = SALFactory(self)

    def zeroNodeInstall_OVH(self, OVHHostName, OVHClient, zerotierNetworkID, zerotierClient):
        """

        OVHHostName is server name as known by OVH

        get clients as follows:
        - zerotierClient = j.clients.zerotier.get(instance='main', data={'data': ZT_API_TOKEN})
        - OVHClient = j.clients.ovh.get(...)

        """

        cl = OVHClient

        self.logger.debug("booting server {} to zero-os".format(OVHHostName))
        task = cl.zero_os_boot(target=OVHHostName, zerotierNetworkID=zerotierNetworkID)
        self.logger.debug("waiting for {} to reboote".format(OVHHostName))
        cl.server_wait_reboot(OVHHostName, task['taskId'])
        ip_pub = cl.server_detail_get(OVHHostName)["ip"]
        self.logger.info("ip addr is:%s" % ip_pub)

        while True:
            try:
                network = zerotierClient.get_network(network_id=zerotierNetworkID)
                member = network.member_get(public_ip=ip_pub)
                ipaddr_priv = member.private_ip
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                self.logger.error(e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                self.logger.error("please authorize the server with the public ip %s in the zerotier network" % ip_pub)
                time.sleep(1)

        self.logger.debug("server found: %s" % member['id'])
        self.logger.debug("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv

    def zeroNodeInstall_PacketNET(self, packetnetClient, zerotierClient, project_name,
                                  plan_type, location, server_name, zerotierNetworkID, ipxe_base='https://bootstrap.gig.tech/ipxe/master'):
        """
        packetnetClient = j.clients.packetnet.get('TOKEN')
        zerotierClient = j.clients.zerotier.get(instance='main', data={'token': 'TOKEN'})
        project_name = packet.net project
        plan_type: one of "Type 0", "Type 1", "Type 2" ,"Type 2A", "Type 3", "Type S"
        location: one of "Amsterdam", "Tokyo", "Synnuvale", "Parsippany"
        server_name: name of the server that is going to be created
        zerotierNetworkID: zertotier network id
        ipxe_base: change this to the version you want, use master branch by default
        """

        valid_plan_types = ("Type 0", "Type 1", "Type 2",
                            "Type 2A", "Type 3", "Type S")  # FIXME
        if plan_type not in valid_plan_types:
            j.exceptions.Input("bad plan type %s. Valid plan type are %s" % (
                plan_type, ','.join(valid_plan_types)))

        if zerotierNetworkID:
            ipxe_url = "%s/%s" % (ipxe_base, zerotierNetworkID)
        else:
            ipxe_url = None

        hostname = server_name

        # find project id
        project_ids = [project.id for project in packetnetClient.projects if project.name == project_name]
        if not project_ids:
            raise j.exceptions.NotFound(
                'No projects found with name %s' % project_name)
        project_id = project_ids[0]
        packetnetClient.project_id = project_id

        packetnetClient.startDevice(hostname=server_name, plan=plan_type, facility=location, os='ubuntu_17_04',
                                    ipxeUrl=ipxe_url, wait=True, remove=False)

        device = packetnetClient.getDevice(server_name)
        ip_pub = [netinfo['address'] for netinfo in device.ip_addresses if netinfo['public'] and netinfo['address_family'] == 4]

        while True:
            try:
                network = zerotierClient.get_network(network_id=zerotierNetworkID)
                member = network.member_get(public_ip=ip_pub[0])
                ipaddr_priv = member.private_ip
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                self.logger.error(e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                self.logger.error("please authorize the server with the public ip %s in the zerotier network" % ip_pub[0])
                time.sleep(1)

        self.logger.debug("server found: %s" % device.id)
        self.logger.debug("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv


class SALFactory:

    def __init__(self, factory):
        self._factory = factory
        self.tfchain = TfChain()

    def get_node(self, instance='main'):
        client = self._factory.get(instance)
        return Node(client)

    def get_minio(self, name, node, login, password, zdbs, namespace, private_key, namespace_secret='', node_port=DEFAULT_PORT, block_size=1048576, restic_username='', restic_password='', meta_private_key=''):
        return Minio(name, node, login, password, zdbs, namespace, private_key, namespace_secret, node_port, block_size, restic_username, restic_password, meta_private_key)

    def get_mongodb(self, name, node, container_name=None, config_replica_set=None, config_port=None, config_mount=None, shard_replica_set=None, shard_port=None, shard_mount=None, route_port=None):
        return Mongodb(name, node, container_name, config_replica_set, config_port, config_mount, shard_replica_set, shard_port, shard_mount, route_port)

    def get_mongos(self, container, port):
        return Mongos(container, port)

    def get_mongod(self, container, replica_set, port, dir, db_type):
        return Mongod(container, replica_set, port, dir, db_type)

    def get_restic(self, container, repo):
        return Restic(container, repo)

    def get_vm(self, hypervisor_name, node):
        return VM(hypervisor_name, node)

    def get_zerorobot(self, container, port=6600, telegram_bot_token=None, telegram_chat_id=0, template_repos=None, data_repo=None, config_repo=None, config_key=None, organization=None, auto_push=None, auto_push_interval=None):
        return ZeroRobot(container, port, telegram_bot_token, telegram_chat_id, template_repos, data_repo, config_repo, config_key, organization=organization, auto_push=auto_push, auto_push_interval=auto_push_interval)

    def format_ports(self, ports):
        """
        Formats ports from ["80:8080"] to {80: 8080}
        :param ports: list of ports to format
        :return: formated ports dict
        """
        if ports is None:
            return {}
        formatted_ports = {}
        for p in ports:
            src, dst = p.split(":")
            formatted_ports[int(src)] = int(dst)

        return formatted_ports

    def __getattr__(self, name):
        if name == 'node_get':
            def wrapper(*args, **kwargs):
                return self.get_node(*args, **kwargs)
            logger.warning("'node_get' is deprecated, please use 'get_node'")
            return wrapper

        return self.__getattribute__(name)
