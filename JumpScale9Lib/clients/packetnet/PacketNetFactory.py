from js9 import j

import packet
import time


class PacketNet():

    def __init__(self, client, projectname=""):
        self.client = client
        self._plans = None
        self._facilities = None
        self._oses = None
        self._projects = None
        self._projectid = None
        self._devices = None
        self.projectname = projectname
        self.logger = j.logger.get('j.clients.packetnet')

 

    @property
    def projectid(self):
        if self._projectid == None:
            if self.projectname is not "":
                for item in self.projects:
                    if item.name == self.projectname:
                        self._projectid = item.id
                        return self._projectid
                raise RuntimeError(
                    "did not find project with name:%s" % self.projectname)
            else:
                res = [item[0] for key, item in self.getProjects().items()]
                if len(res) == 1:
                    self._projectid = res[0]
                else:
                    raise RuntimeError("found more than 1 project")
        return self._projectid

    @property
    def plans(self):
        if self._plans == None:
            self._plans = self.client.list_plans()
        return self._plans

    @property
    def facilities(self):
        if self._facilities == None:
            self._facilities = self.client.list_facilities()
        return self._facilities

    @property
    def operatingsystems(self):
        if self._oses == None:
            self._oses = self.client.list_operating_systems()
        return self._oses

    @property
    def projects(self):
        if self._projects == None:
            self._projects = self.client.list_projects()
        return self._projects

    @property
    def devices(self):
        if self._devices == None:
            self._devices = self.client.list_devices(self.projectid)
        return self._devices

    def getPlans(self):
        res = {}
        for plan in self.plans:
            res[plan.slug] = (plan.name, plan.specs)
        return res

    def getFacilities(self):
        res = {}
        for item in self.facilities:
            res[item.code] = item.name
        return res

    def getOperatingSystems(self):
        res = {}
        for item in self.operatingsystems:
            res[item.slug] = (item.name, item.distro,
                              item.version, item.provisionable_on)
        return res

    def getProjects(self):
        res = {}
        for item in self.projects:
            res[item.name] = (item.id, item.devices)
        return res

    def getDevices(self):
        res = {}
        for item in self.devices:
            res[item.hostname] = item
        return res

    def getDevice(self, name, id=None, die=False):
        if id == None:
            if name in [item for item in self.getDevices().keys()]:
                return self.getDevices()[name]
            if die == False:
                return None
        else:
            return self.client.get_device(id)

        raise RuntimeError("could not find device:%s" % name)

    def removeDevice(self, name):
        res = self.getDevice(name)
        if res != None:
            self._devices = None
            print("found machine, remove:%s" % name)
            res.delete()

    def startDevice(self,  hostname="removeMe", plan='baremetal_0', facility='ams1', os='ubuntu_17_04', ipxeUrl=None, wait=True, remove=False):
        """
        will delete if it exists when remove=True, otherwise will check if it exists, if yes will return device object
        if not will create

        example ipxeUrl = https://bootstrap.gig.tech/ipxe/zero-os-master-generic
        """

        if ipxeUrl is None:
            zerotierId = ""
        else:
            zerotierId = ipxeUrl.split('/')[-1]
        return self._startDevice(hostname=hostname, plan=plan, facility=facility, os=os,
                                 wait=wait, remove=remove, ipxeUrl=ipxeUrl, zerotierId=zerotierId, always_pxe=False)

    def startZeroOS(self, hostname="removeMe", plan='baremetal_0', facility='ams1', zerotierId="", zerotierAPI="", wait=True, remove=False):
        """
        return (zero-os-client,pubIpAddress,zerotierIpAddress)
        """
        if zerotierId.strip() == "" or zerotierId is None:
            raise RuntimeError("zerotierId needs to be specified")
        if zerotierAPI.strip() == "" or zerotierAPI is None:
            raise RuntimeError("zerotierAPI needs to be specified")
        ipxeUrl = "https://bootstrap.gig.tech/ipxe/master/%s" % zerotierId

        ipaddr = self._startDevice(hostname=hostname, plan=plan, facility=facility, os="",
                                   wait=wait, remove=remove, ipxeUrl=ipxeUrl, zerotierId=zerotierId, always_pxe=True)

        zerotierClient = j.clients.zerotier.get(zerotierAPI)

        while True:
            try:
                member = zerotierClient.networkMemberGetFromIPPub(
                    ipaddr, networkId=zerotierId, online=True)
                ipaddr_priv = member["ipaddr_priv"][0]
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                print("[-] %s" % e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                print(
                    "[+] please authorize the server with the public ip %s in the zerotier network" % ipaddr)
                time.sleep(1)

        print("[+] zerotier IP: %s" % ipaddr_priv)
        zosclient = j.clients.zero_os.get(ipaddr_priv)
        return zosclient, ipaddr, ipaddr_priv

    def _startDevice(self,  hostname="removeMe", plan='baremetal_0', facility='ams1',
                     os='ubuntu_17_04', wait=True, remove=True, ipxeUrl=None, zerotierId="", always_pxe=False):
        """
        will delete if it exists when remove=True, otherwise will check if it exists, if yes will return device object
        if not will create

        example ipxeUrl = https://bootstrap.gig.tech/ipxe/zero-os-master-generic
        """

        if ipxeUrl is None:
            ipxeUrl = ""
        if remove:
            self.removeDevice(hostname)

        device = self.getDevice(hostname)
        if device is None:
            device = self.client.create_device(project_id=self.projectid,
                                               hostname=hostname,
                                               plan=plan, facility=facility,
                                               operating_system=os, ipxe_script_url=ipxeUrl, always_pxe=False)
            self._devices = None

        res = device.update()
        while res["state"] not in ["active"]:
            res = device.update()
            time.sleep(1)
            print(res["state"])

        ipaddr = [netinfo['address']
                  for netinfo in res["ip_addresses"] if netinfo['public'] and netinfo['address_family'] == 4]

        ipaddr = ipaddr[0]

        print("ipaddress found = %s" % ipaddr)

        if zerotierId == "":
            print("test ssh port & wait")
            j.sal.nettools.waitConnectionTest(ipaddr, 22, 60)
            print("ssh answered")

            ssh = j.clients.ssh.get(addr=ipaddr)

            ssh.execute("ls /")

            return device, ssh.prefab

        j.tools.develop.nodes.nodeSet(name=hostname, addr=ipaddr, port=22, cat='packet', description='', selected=True)

        return ipaddr

    def addSSHKey(self, sshkeyPub):
        raise RuntimeError("not implemented")


TEMPLATE = """
auth_token_ = ""
"""

BASE = j.tools.secretconfig.base_class_secret

class PacketNetFactory(BASE):

    def __init__(self):
        self.__jslocation__ = "j.clients.packetnet"
        self.__imports__ = "packet"
        self.logger = j.logger.get('j.clients.packetnet')
        self.connections = {}
        self.instance="main"
        self._TEMPLATE=TEMPLATE

    def install(self):
        j.sal.process.execute("pip3 install packet-python")

    def get(self,instance="main"):
        self.instance=instance
        from IPython import embed;embed(colors='Linux')
        return PacketNet(packet.Manager(auth_token=self.config.data["auth_token"]))

    def test(self):
        from IPython import embed;embed(colors='Linux')
