from js9 import j

import ovh
import requests
import time


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
        j.do.execute(cmd)

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

        return ip_pub, ipaddr_priv

    def zeroNodeInstall_PacketNET(self, packetnetClient):
        pass
