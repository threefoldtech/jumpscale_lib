from js9 import j

import ovh
import requests
import time

# class OVHServer:
#
#     def __init__(self,ovhclient,name):
#         self.ovhclient=ovhclient
#         self.name=name
#
#     def reload(self):
#         from IPython import embed
#         print ("DEBUG NOW kk")
#         embed()
#         raise RuntimeError("stop debug here")


class OVHClient:

    def __init__(self, appkey, appsecret, consumerkey="", endpoint='soyoustart-eu', ipxeBase="https://bootstrap.gig.tech/ipxe/master"):
        # if consumerkey=="":
        #     client = ovh.Client(endpoint=endpoint)
        #     ck = client.new_consumer_key_request()
        #     ck.add_recursive_rules(ovh.API_READ_WRITE, '/')
        print("OVH INIT")
        self.client = ovh.Client(
            endpoint=endpoint,
            application_key=appkey,
            application_secret=appsecret,
            consumer_key=consumerkey,
        )

        id = "ovhclient_%s" % consumerkey
        self.cache = j.data.cache.get(
            id=id,
            db=j.data.kvs.getRedisStore())
        self.ipxeBase = ipxeBase.rstrip("/")

    def nameCheck(self, name):
        if "ns302912" in name:
            raise RuntimeError("Cannot use server:%s" % name)

    def reset(self):
        self.cache.reset()

    def installationTemplates(self):
        def getData():
            print("get installationTemplates")
            return self.client.get('/dedicated/installationTemplate')
        return self.cache.get("installationTemplates", getData, expire=3600)

    def sshKeysGet(self):
        def getData():
            print("get sshkeys")
            return self.client.get('/me/sshKey')
        return self.cache.get("sshKeys", getData)

    def sshKeyAdd(self, name, key):
        """
        @param name: name of the new public SSH key
        @param key: ASCII encoded public SSH key to add
        """
        return self.client.post('/me/sshkey', keyName=name, key=key)

    def serversGetList(self):
        def getData():
            print("get serversList")
            llist = self.client.get("/dedicated/server")
            llist = [item for item in llist if item.find("ns302912") == -1]
            return llist
        return self.cache.get("serversList", getData)

    # def getETCDConnectionFromCluster(self):
    #     """
    #     will check ssh on each server, when ssh found then check if there is an ETCD server installed
    #     if not will install
    #     if yes will return
    #     """
    #     l = []
    #     for item in self.serversGetList():
    #         try:
    #             l.append(self.prefabGet(item))
    #         except:
    #             pass
    #     from IPython import embed
    #     print("DEBUG NOW sdsd")
    #     embed()
    #     raise RuntimeError("stop debug here")

    def serverGetDetail(self, name, reload=False):
        self.nameCheck(name)
        key = "serverGetDetail_%s" % name
        if reload:
            self.cache.delete(key)

        def getData(name):
            # print("get %s" % key)
            return self.client.get("/dedicated/server/%s" % name)
        return self.cache.get(key, getData, name=name, expire=120)

    def serverGetInstallStatus(self, name, reload=False):
        self.nameCheck(name)
        key = "serverGetInstallStatus%s" % name
        if reload:
            self.cache.delete(key)

        def getData(name):
            print("get %s" % key)
            try:
                return self.client.get("/dedicated/server/%s/install/status" % name)
            except Exception as e:
                if "Server is not being installed or reinstalled at the moment" in str(e):
                    return "active"
                else:
                    raise e
        return self.cache.get(key, getData, name=name, expire=120)

    def serversGet(self):
        res = []
        for item in self.serversGetList():
            res.append((item, self.serverGetDetail(item)))
        return res

    def prefabGet(self, name):
        self.nameCheck(name)
        details = self.serverGetDetail(name)
        e = j.tools.executor.get(details["ip"])
        return e.prefab

    # def backupInit(self, name):
    #     try:
    #         self.client.post("/dedicated/server/%s/features/backupFTP" % name)
    #     except Exception as e:
    #         if "You already have a backupFTP" in str(e):
    #             print("backup init already done for %s" % name)
    #             return "ALREADYOK"
    #         else:
    #             raise e
    #     print("backup init ok for %s" % name)
    #     return "OK"
    #
    # def backupGet(self, name):
    #     try:
    #         res = self.client.get("/dedicated/server/%s/features/backupFTP" % name)
    #     except Exception as e:
    #         if "The requested object (backupFTP) does not exist" in str(e):
    #             print("backup was not inited yet for %s" % name)
    #             self.backupInit(name)
    #             res = self.client.get("/dedicated/server/%s/features/backupFTP" % name)
    #         else:
    #             raise e
    #     return res

    def prefabsGet(self):
        """
        return all prefab connections to all known servers

        returns [(name,prefab),]
        """
        res = []
        for name in self.serversList:
            details = self.serverGetDetail(name)
            e = j.tools.executor.get(details["ip"])
            res.append((name, e.prefab))
        return res

    def serversWaitInstall(self):
        nrInstalling = 1
        while nrInstalling > 0:
            nrInstalling = 0
            for item in self.serversGetList():
                status = self.serverGetInstallStatus(name=item, reload=True)
                key = "serverGetDetail_%s" % item  # lets make sure server is out of cache too
                self.cache.delete(key)
                if status != "active":
                    print(item)
                    print(j.data.serializer.yaml.dumps(status))
                    print("-------------")
                    nrInstalling += 1
            time.sleep(2)
        self.details = {}
        print("INSTALL DONE")

    def serverInstall(self, name="", installationTemplate="ubuntu1704-server_64", sshKeyName="ovh",
                      useDistribKernel=True, noRaid=True, hostname="", wait=True):
        """
        if name == * then will install on all and names will be the name given by ovh

        """
        self.nameCheck(name)
        if installationTemplate not in self.installationTemplates():
            raise j.exceptions.Input(message="could not find install template:%s" %
                                     templateName, level=1, source="", tags="", msgpub="")
        if sshKeyName not in self.sshKeysGet():
            raise j.exceptions.Input(message="could not find sshKeyName:%s" %
                                     sshKeyName, level=1, source="", tags="", msgpub="")

        if name == "*":
            for item in self.serversGetList():
                self.serverInstall(name=item, wait=False)
            wait = True
        elif name == "":
            raise j.exceptions.Input(
                message="please specify name", level=1, source="", tags="", msgpub="")
        else:
            if hostname == "":
                hostname = name
            details = {}
            details["installationTemplate"] = installationTemplate
            details["useDistribKernel"] = useDistribKernel
            details["noRaid"] = noRaid
            details["customHostname"] = hostname
            details["sshKeyName"] = sshKeyName

            # make sure cache for this server is gone
            key = "serverGetDetail_%s" % name
            self.cache.delete(key)

            try:
                self.client.post("/dedicated/server/%s/install/start" %
                                 name, details=details, templateName=installationTemplate)
            except Exception as e:
                if "A reinstallation is already in todo" in str(e):
                    print("INFO:%s:%s" % (name, e))
                    pass
                else:
                    raise e

        if wait:
            self.serversWaitInstall()

        if name == "":
            self.details = {}
        else:
            if name in self.details:
                self.details.pop(name)

    def listNetworkBootloader(self):
        """
        Lists iPXE scripts installed on the account
        """
        return self.client.get("/me/ipxeScript")

    def inspectNetworkBootloader(self, name):
        """
        Returns contents of the iPXE script name given in parameter
        """
        return self.client.delete("/me/ipxeScript/%s" % name)

    def deleteNetworkBootloader(self, name):
        """
        Delete a iPXE script boot entry
        Note: this require DELETE account capability
        """
        return self.client.delete("/me/ipxeScript/%s" % name)

    def installNetworkBootloader(self, ipxe):
        """
        Set a new iPXE boot script bootloader
        ipxe: should contains a dictionary with:
          - description: a description which will be displayed on the summary page
          - name: a name which will identify the iPXE script entry
          - script: the iPXE script which will be executed during the boot
        """
        return self.client.post("/me/ipxeScript", **ipxe)

    def isBootAvailable(self, name):
        """
        Checkk if an iPXE boot script name already exists
        """
        existing = self.listNetworkBootloader()

        for item in existing:
            if item == name:
                return True

        return None

    def _setBootloader(self, target, bootid):
        print("[+] bootloader selected: %s" % bootid)

        payload = {"bootId": int(bootid)}
        self.client.put("/dedicated/server/%s" % target, **payload)

        return True

    def setBootloader(self, target, name):
        """
        Set and apply an iPXE boot script to a remote server
        - target: need to be a OVH server hostname
        - name: need to be an existing iPXE script name
        """
        bootlist = self.client.get(
            "/dedicated/server/%s/boot?bootType=ipxeCustomerScript" % target)
        checked = None

        for bootid in bootlist:
            data = self.client.get(
                "/dedicated/server/%s/boot/%s" % (target, bootid))
            if data['kernel'] == name:
                return self._setBootloader(target, bootid)

        return False

    def reboot(self, name):
        """
        Reboot a server
        - target: need to be a OVH server hostname
        """
        self.nameCheck(name)
        return self.client.post("/dedicated/server/%s/reboot" % name)

    #
    # custom builder
    #
    def _zos_build(self, url):
        """
        Internal use.
        This build an OVH adapted iPXE script based on an officiel bootstrap URL
        """
        # strip trailing flash
        url = url.rstrip('/')
        print("zero hub url:%s" % url)
        # downloading original ipxe script
        try:
            script = requests.get(url)
        except Exception as e:
            msg = "ERROR: zerohub server does not respond\nError:\n%s\n" % e
            raise(msg)
        if script.status_code != 200:
            raise RuntimeError("Invalid script URL")

        # going unsecure, because ovh
        fixed = script.text.replace(
            'https://bootstrap.', 'http://unsecure.bootstrap.')

        # setting name and description according to the url
        fields = url.split('/')

        if len(fields) == 7:
            # branch name, zerotier network, arguments
            description = "Zero-OS: %s (%s, %s)" % (
                fields[4], fields[5], fields[6])
            name = "zero-os-%s-%s,%s" % (fields[4], fields[5], fields[6])

        elif len(fields) == 6:
            # branch name, zerotier network, no arguments
            description = "Zero-OS: %s (%s, no arguments)" % (
                fields[4], fields[5])
            name = "zero-os-%s-%s" % (fields[4], fields[5])

        else:
            # branch name, no zerotier, no arguments
            description = "Zero-OS: %s (no zerotier, no arguments)" % fields[4]
            name = "zero-os-%s" % fields[4]

        return {'description': description, 'name': name, 'script': fixed}

    def zeroOSBoot(self, target, zerotierNetworkID):
        """
        Configure a node to use Zero-OS iPXE kernel
        - target: need to be an OVH server hostname
        - zerotierNetworkID: network to be used in zerotier
        """
        self.nameCheck(target)
        url = "%s/%s" % (self.ipxeBase, zerotierNetworkID)
        ipxe = self._zos_build(url)

        print("[+] description: %s" % ipxe['description'])
        print("[+] boot loader: %s" % ipxe['name'])

        if not self.isBootAvailable(ipxe['name']):
            print("[+] installing the bootloader")
            self.installNetworkBootloader(ipxe)
        self.setBootloader(target, ipxe['name'])
        return self.reboot(target)

    def getTask(self, target, taskId):
        return self.client.get("/dedicated/server/%s/task/%s" % (target, taskId))

    def waitServerReboot(self, target, taskId):
        current = ""

        while True:
            status = self.getTask(target, taskId)

            if status['status'] != current:
                current = status['status']
                print("[+] rebooting %s: %s" % (target, current))

            if status['status'] == 'done':
                return True

            time.sleep(1)


class OVHFactory:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.ovh"
        self.__imports__ = "ovh"
        self.logger = j.logger.get('j.clients.ovh')
        self.connections = {}

    def get(self, appkey, appsecret, consumerkey="", endpoint='soyoustart-eu'):
        """
        Visit https://eu.api.soyoustart.com/createToken/

        IMPORTANT:
        for rights add get,post,put & delete rights
        for each of them put /*
        this will make sure you have all rights on all methods recursive

        to get your credentials

        endpoints:
            ovh-eu for OVH Europe API
            ovh-ca for OVH North-America API
            soyoustart-eu for So you Start Europe API
            soyoustart-ca for So you Start North America API
            kimsufi-eu for Kimsufi Europe API
            kimsufi-ca for Kimsufi North America API
            runabove-ca for RunAbove API

        """
        return OVHClient(appkey=appkey, appsecret=appsecret, consumerkey=consumerkey, endpoint=endpoint)

    def getByName(self, name):
        """
        name is in j.core.config[$name] and can be set with something listNetworkBootloader

        js9 'j.core.state.configSetInDict("ovh_gig","appsecret","xxx")'
        js9 'j.core.state.configSetInDict("ovh_gig","appkey","xxx")'
        js9 'j.core.state.configSetInDict("ovh_gig","consumerkey","xxx")'
        js9 'j.core.state.configSetInDict("ovh_gig","endpoint","soyoustart-eu")'

        """
        cl = j.clients.ovh.get(appkey=j.core.state.configGetFromDict(name, "appkey"),
                               appsecret=j.core.state.configGetFromDict(
                                   name, "appsecret"),
                               consumerkey=j.core.state.configGetFromDict(name, "consumerkey"))

        return cl
