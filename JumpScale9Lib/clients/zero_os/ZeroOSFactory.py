import time

from js9 import j

from .Client import Client
from .sal.Node import Node

JSConfigFactoryBase = j.tools.configmanager.base_class_configs


class ZeroOSFactory(JSConfigFactoryBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zero_os"
        super().__init__(Client)
        self.logger = j.logger.get('j.clients.zero-os')
        self.connections = {}
        self.sal = SALFactory(self)

    def zeroNodeInstall_OVH(self, OVHServerID, OVHClient, zerotierNetworkID, zerotierClient):
        """

        OVHServerID is server id as known by OVH

        get clients as follows:
        - zerotierClient = j.clients.zerotier.get(ZT_API_TOKEN)
        - OVHClient = j.clients.ovh.get(...)

        """

        cl = OVHClient
        zt = zerotierClient

        self.logger.debug("booting server {} to zero-os".format(OVHServerID))
        task = cl.zeroOSBoot(target=OVHServerID, zerotierNetworkID=zerotierNetworkID)
        self.logger.debug("waiting for {} to reboote".format(OVHServerID))
        cl.waitServerReboot(OVHServerID, task['taskId'])
        ip_pub = cl.serverGetDetail(OVHServerID)["ip"]
        self.logger.info("ip addr is:%s" % ip_pub)

        while True:
            try:
                member = zt.getNetworkMemberFromIPPub(
                    ip_pub, networkId=zerotierNetworkID, online=True)
                ipaddr_priv = member["ipaddr_priv"][0]
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
        zerotierClient = j.clients.zerotier.get('TOKEN')
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
                member = zerotierClient.networkMemberGetFromIPPub(ip_pub[0], networkId=zerotierNetworkID, online=True)
                ipaddr_priv = member["ipaddr_priv"][0]
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

    def node_get(self, instance='main'):
        client = self._factory.get(instance)
        return Node(client)
