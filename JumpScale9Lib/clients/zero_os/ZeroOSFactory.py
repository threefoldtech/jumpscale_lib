from js9 import j
from zeroos.orchestrator.sal.Node import Node
import ovh
import requests
import time


class ZeroOS:
    def __init__(self, node):
        self.node = node
        self.client = node.client

    def allow_port_tcp(self, port, interface=None, subnet=None):
        for item in self.client.nft.list():
            if item.startswith("tcp") and "accept" in item and str(port) in item:
                return True
        self.client.nft.open_port(port)
        return True

    def prepare_disks(self,  name="fscache", wipedisks=False):
        """
        if exists will return, if not will create
        when wipedisks used will reset the disks (CAREFUL)
        """
        print("[+] prepare disks")
        if wipedisks:
            self.node.wipedisks()

        res = self.node.find_persistance(name=name)
        if res is not None:
            return res
        else:
            res = self.node.ensure_persistance(name=name)
        return res

    def install(self):
        j.sal.process.execute("pip3 install 0-orchestrator")


class ZeroOSFactory:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zero_os"
        self.__imports__ = "ovh"
        self.logger = j.logger.get('j.clients.ovh')
        self.connections = {}

    def client_install(self):
        cmd = """
        export CORE_BRANCH="master"
        export ORCHESTRATOR_BRANCH="master"
        pip3 install -U "git+https://github.com/zero-os/0-core.git@${CORE_BRANCH}#subdirectory=client/py-client"
        pip3 install -U "git+https://github.com/zero-os/0-orchestrator.git@${ORCHESTRATOR_BRANCH}#subdirectory=pyclient"
        pip3 install -U zerotier
        """
        j.sal.process.execute(cmd)

    def zeroNodeInstall_OVH(self, OVHServerID, OVHClient, zerotierNetworkID, zerotierClient):
        """

        OVHServerID is server id as known by OVH

        get clients as follows:
        - zerotierClient = j.clients.zerotier.get(ZT_API_TOKEN)
        - OVHClient = j.clients.ovh.get(...)

        """

        cl = OVHClient
        zt = zerotierClient

        print("[+] booting server " + OVHServerID + " to zero-os")
        task = cl.zeroOSBoot(target=OVHServerID,
                             zerotierNetworkID=zerotierNetworkID)
        print("[+] waiting " + OVHServerID + " for reboot")
        cl.waitServerReboot(OVHServerID, task['taskId'])
        ip_pub = cl.serverGetDetail(OVHServerID)["ip"]
        print("[+] ip addr is:%s" % ip_pub)

        while True:
            try:
                member = zt.getNetworkMemberFromIPPub(
                    ip_pub, networkId=zerotierNetworkID, online=True)
                ipaddr_priv = member["ipaddr_priv"][0]
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                print("[-] %s" % e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                print(
                    "[+] please authorize the server with the public ip %s in the zerotier network" % ip_pub)
                time.sleep(1)

        print("[+] server found: %s" % member['id'])
        print("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv

    def zeroNodeInstall_PacketNET(self, packetnetClient, zerotierClient, project_name, plan_type, location, server_name, zerotierNetworkID, ipxe_base='https://bootstrap.gig.tech/ipxe/master'):
        """
        packetnetClient = packet = j.clients.packetnet.get('TOKEN')
        zerotierClient = j.clients.zerotier.get('TOKEN')
        project_name = packet.net project
        plan_type: one of "Type 0", "Type 1", "Type 2" ,"Type 2A", "Type 3", "Type S"
        location: one of "Amsterdam", "Tokyo", "Synnuvale", "Parsippany"
        server_name: name of the server that is going to be created
        zerotierNetworkID: zertotier network id
        ipxe_base: change this to the version you want, use master branch by default
        """

        valid_plan_types = ("Type 0", "Type 1", "Type 2",
                            "Type 2A", "Type 3", "Type S")
        if plan_type not in valid_plan_types:
            j.exceptions.Input("bad plan type %s. Valid plan type are %s" % (
                plan_type, ','.join(valid_plan_types)))

        ipxe_url = "%s/%s" % (ipxe_base, zerotierNetworkID)

        hostname = server_name

        # find project id
        project_ids = [project.id for project in packetnetClient.list_projects(
        ) if project.name == project_name]
        if not project_ids:
            raise j.exceptions.NotFound(
                'No projects found with name %s' % project_name)
        project_id = project_ids[0]

        # find service type id
        project_devices = {
            device.hostname: device for device in packetnetClient.list_devices(project_id)}
        if hostname not in project_devices:
            plan_ids = [plan.id for plan in packetnetClient.list_plans()
                        if plan.name == plan_type]
            if not plan_ids:
                raise j.exceptions.NotFound(
                    'No plans found with name %s' % plan_type)
            plan_id = plan_ids[0]

            # find facility id
            facility_id = None
            for facility in packetnetClient.list_facilities():
                if facility.name.lower().find(location.lower()) != -1:
                    facility_id = facility.id

            if facility_id is None:
                raise j.exceptions.Input(
                    message="Could not find facility in packet.net:%s" % location)
            try:
                device = packetnetClient.create_device(project_id=project_id, hostname=hostname, plan=plan_id,
                                                       facility=facility_id, operating_system='custom_ipxe', ipxe_script_url=ipxe_url)
            except Exception as e:
                if "Service Unavailable" in str(e):
                    raise j.exceptions.Input(
                        message="could not create packet.net machine, type of machine not available")
                raise e
        else:
            device = project_devices[hostname]

        print("[+] booting server ", end='')
        timeout_start = time.time()
        timeout = 900
        while time.time() < timeout_start + timeout and device.state != 'active':
            time.sleep(5)
            device = packetnetClient.get_device(device.id)
            print('.', end='')

        if device.state != 'active':
            raise RuntimeError('Too long to provision')

        ip_pub = [netinfo['address']
                  for netinfo in device.ip_addresses if netinfo['public'] and netinfo['address_family'] == 4]

        while True:
            try:
                member = zerotierClient.getNetworkMemberFromIPPub(
                    ip_pub[0], networkId=zerotierNetworkID, online=True)
                ipaddr_priv = member["ipaddr_priv"][0]
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                print("[-] %s" % e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                print(
                    "[+] please authorize the server with the public ip %s in the zerotier network" % ip_pub[0])
                time.sleep(1)

        print("[+] server found: %s" % device.id)
        print("[+] zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv

    def get(self, ip_priv):
        print("[+] contacting zero-os server: %s" % ip_priv)

        print("[+] check port: 6379")
        res = j.sal.nettools.waitConnectionTest(ip_priv, 6379, 90)
        if res is False:
            msg = "[+] make sure you are authorized in the zertotier network"
            raise RuntimeError(msg)

        node = Node(ip_priv)
        node.client.timeout = 180

        return ZeroOS(node)
