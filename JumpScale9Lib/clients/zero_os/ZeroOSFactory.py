from js9 import j
# from zeroos.orchestrator.sal.Node import Node
import ovh
import requests
import time

from .Client import *
# class ZeroOSClient:
#     def __init__(self, client):
#         self._client = client
#         self.logger = 
#         self.aggregator = AggregatorManager(self._client )
#         self.bridges = BridgeManager(self._client )
#         self.btrfs = BtrfsManager(self._client )
#         self.config = Config(self._client )
#         self.containers = ContainerManager(self._client )
#         self.disks = DiskManager(self._client )
#         self.filesystem = FilesystemManager(self._client )
#         self.ip = IPManager(self._client )
#         self.kvm = KvmManager(self._client )
#         self.logs = LogManager(self._client )
#         self.nft = Nft(self._client )
#         self.processes = ProcessManager(self._client )
#         self.zerotier = ZerotierManager(self._client )

#     def allow_port_tcp(self, port, interface=None, subnet=None):
#         for item in self.client.nft.list():
#             if item.startswith("tcp") and "accept" in item and str(port) in item:
#                 return True
#         self.client.nft.open_port(port)
#         return True

#     def prepare_disks(self,  name="fscache", wipedisks=False):
#         """
#         if exists will return, if not will create
#         when wipedisks used will reset the disks (CAREFUL)
#         """
#         print("[+] prepare disks")
#         if wipedisks:
#             self.node.wipedisks()

#         res = self.node.find_persistance(name=name)
#         if res is not None:
#             return res
#         else:
#             res = self.node.ensure_persistance(name=name)
#         return res


class ZeroOSFactory:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zero_os"
        self.logger = j.logger.get('j.clients.zero-os')
        self.connections = {}

    # def client_install(self):
    #     cmd = """
    #     export CORE_BRANCH="master"
    #     export ORCHESTRATOR_BRANCH="master"
    #     pip3 install -U "git+https://github.com/zero-os/0-core.git@${CORE_BRANCH}#subdirectory=client/py-client"
    #     pip3 install -U "git+https://github.com/zero-os/0-orchestrator.git@${ORCHESTRATOR_BRANCH}#subdirectory=pyclient"
    #     pip3 install -U zerotier
    #     """
    #     j.sal.process.execute(cmd)

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

    def zeroNodeInstall_PacketNET(self, packetnetClient, zerotierClient, project_name, \
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
                            "Type 2A", "Type 3", "Type S") #FIXME
        if plan_type not in valid_plan_types:
            j.exceptions.Input("bad plan type %s. Valid plan type are %s" % (
                plan_type, ','.join(valid_plan_types)))

        ipxe_url = "%s/%s" % (ipxe_base, zerotierNetworkID)

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

    def get(self, host, port=6379, password="", db=0, ssl=True, timeout=None, testConnectionAttempts=3):
        # super().__init__(timeout=timeout)):

        self.logger.info("[+] contacting zero-os server:{}".format(host))

        self.logger.info("[+] check port:{}".format(port))
        res = j.sal.nettools.waitConnectionTest(host, port, 90)
        if res is False:
            msg = "[+] make sure you are authorized in the zertotier network"
            raise RuntimeError(msg)

        client=Client(host=host, port=port, password=password, db=db, \
            ssl=ssl, timeout=timeout, testConnectionAttempts=testConnectionAttempts)


        return ZeroOSClient(client)
