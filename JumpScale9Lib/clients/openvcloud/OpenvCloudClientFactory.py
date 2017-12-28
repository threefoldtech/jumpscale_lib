from js9 import j
import time
import datetime
import os
import requests

# NEED: pip3 install python-jose


def refresh_jwt(jwt, payload):
    if payload['iss'] == 'itsyouonline':
        refreshurl = "https://itsyou.online/v1/oauth/jwt/refresh"
        response = requests.get(refreshurl, headers={
                                'Authorization': 'bearer {}'.format(jwt)})
        if response.ok:
            return response.text
        else:
            raise RuntimeError("Failed to refresh JWT eror: {}:{}".format(
                response.status_code, response.text))
        pass
    else:
        raise RuntimeError(
            'Refresh JWT with issuers {} not support'.format(payload['iss']))


class OpenvCloudClientFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"

    def install(self):
        j.sal.process.execute("pip3 install python-jose")

    def _urlClean(self, url):
        url = url.lower()
        if url.startswith("http"):
            url = url.split("//")[1].rstrip("/")
        print("Get OpenvCloud client on URL: %s" % url)
        return url

    def get(self, applicationId, secret, url):
        """
        Returns an OpenvCloud Client object for a given application ID and secret.

        Get the application ID and secret by creating an API key on the settings page of your user profile on https://itsyou.online.

        Args:
            - applicationId: application ID of the API key as set in ItsYou.online for your user profile
            - secret: secret part of the API key as set in ItsYou.online for your user profile
            - url: base url of the OpenvCloud environment, e.g. https://se-gen-1.demo.greenitglobe.com/
        """
        url = self._urlClean(url)
        jwt = self.getJWTTokenFromItsYouOnline(applicationId, secret)
        login = None
        password = None
        port = 443
        cl = Client(url, login, password, secret, port, jwt)
        return cl

    def getLegacy(self, url, login=None, password=None, port=443, jwt=None):
        """
        Returns an OpenvCloud Client object for a given username and password.

        Only use this for legacy purposes or in private deployments where ItsYou.online is not used.

        It is highly recommended to use the get() method instead, passing an application ID and secret from ItsYou.online.

        Args:
            url: base url of the OpenvCloud environment, e.g. https://se-gen-1.demo.greenitglobe.com/
            login: OpenvCloud username
            password: password of the OpenvCloud user
        """

        url = self._urlClean(url)
        cl = Client(url, login, password, secret=None, port=port, jwt=jwt)
        return cl

    def getFromAYSService(self, service):
        """
        Returns an OpenvCloud Client object for a given AYS service object.
        """
        return self.getLegacy(
            url=service.model.data.url,
            login=service.model.data.login,
            password=service.model.data.password,
            jwt=service.model.data.jwt,
            port=service.model.data.port)

    def getJWTTokenFromItsYouOnline(self, applicationId, secret, validity=3600):
        """
        Returns JSON Web token (JWT) for the specified application ID and secret.

        Get the application ID and secret by creating an API key on the settings page of your user profile on https://itsyou.online.

        Args:
            - applicationId: application ID of the API key as set in ItsYou.online for your user profile
            - secret: secret part of the API key as set in ItsYou.online for your user profile
            - validity: (defaults to 3600) duration in seconds that the requested JWT should stay valid
        """

        params = {
            'grant_type': 'client_credentials',
            'response_type': 'id_token',
            'client_id': applicationId,
            'client_secret': secret,
            'validity': validity
        }
        url = 'https://itsyou.online/v1/oauth/access_token'
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt = resp.content.decode('utf8')
        return jwt

class Client:

    def __init__(self, url, login, password=None, secret=None, port=443, jwt=None):
        if not password and not secret and not jwt:
            raise ValueError(
                "Cannot connect to OpenvCloud without either password, secret or JWT")
        self._url = url
        self._login = login
        self._password = password
        self._secret = secret
        self._jwt = jwt
        self.api = j.clients.portal.get(url, port)
        # patch handle the case where the connection dies because of inactivity
        self.__patch_portal_client(self.api)

        self._isms1 = 'mothership1' in url
        self.__login(password, secret, jwt)
        if self._isms1:
            jsonpath = os.path.join(os.path.dirname(__file__), 'ms1.json')
            self.api.load_swagger(file=jsonpath, group='cloudapi')
            patchMS1(self.api)
        else:
            self.api.load_swagger(group='cloudapi')

    def __patch_portal_client(self, api):
        # try to relogin in the case the connection is dead because of
        # inactivity
        origcall = api.__call__

        def patch_call(that, *args, **kwargs):
            from JumpScale9Lib.clients.portal.PortalClient import ApiError
            try:
                return origcall(that, *args, **kwargs)
            except ApiError:
                if ApiError.response.status_code == 419:
                    self.__login(self._password, self._secret, self._jwt)
                    return origcall(that, *args, **kwargs)
                raise

        api.__call__ = patch_call

    def __login(self, password, secret, jwt):
        if not password and not secret and not jwt:
            raise RuntimeError(
                "Cannot connect to OpenvCloud without either password, secret or JWT")
        if jwt:
            import jose.jwt
            payload = jose.jwt.get_unverified_claims(jwt)
            if payload['exp'] < time.time():
                jwt = refresh_jwt(jwt, payload)
            self.api._session.headers['Authorization'] = 'bearer {}'.format(
                jwt)
            self._login = '{}@{}'.format(payload['username'], payload['iss'])
        else:
            if password:
                if self._isms1:
                    secret = self.api.cloudapi.users.authenticate(
                        username=self._login, password=password)
                else:
                    secret = self.api.system.usermanager.authenticate(
                        name=self._login, secret=password)
            # make sure cookies are empty, clear guest cookie
            self.api._session.cookies.clear()
            self.api._session.cookies['beaker.session.id'] = secret

    @property
    def accounts(self):
        ovc_accounts = self.api.cloudapi.accounts.list()
        accounts = list()
        for account in ovc_accounts:
            accounts.append(Account(self, account))
        return accounts

    @property
    def locations(self):
        return self.api.cloudapi.locations.list()

    def account_get(self, name, create=True,
                    maxMemoryCapacity=-1, maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNASCapacity=-1,
                    maxNetworkOptTransfer=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1):
        """
        Returns the OpenvCloud account with the given name, and in case it doesn't exist yet the account will be created.

        Args:
            - name (required): name of the account to lookup or create if it doesn't exist yet, e.g. "myaccount"
            - create (defaults to True): if set to True the account is created in case it doesn't exist yet
            - maxMemoryCapacity (defaults to -1: unlimited): available memory in GB for all virtual machines in the account
            - maxVDiskCapacity (defaults to -1: unlimited): available disk capacity in GiB for all virtual disks in the account
            - maxCPUCapacity (defaults to -1: unlimited): total number of available virtual CPU core that can be used by the virtual machines in the account
            - maxNASCapacity (defaults to -1: unlimited): not implemented
            - maxNetworkOptTransfer (defaults to -1: unlimited): not implemented
            - maxNetworkPeerTransfer (defaults to -1: unlimited): not implemented
            - maxNumPublicIP (defaults to -1: unlimited): number of external IP addresses that can be used in the account

        Raises: KeyError if account doesn't exist, and create argument was set to False
        """
        for account in self.accounts:
            if account.model['name'] == name:
                return account
        else:
            if create is False:
                raise KeyError("No account with name \"%s\" found" % name)
            self.api.cloudbroker.account.create(username=self.login,
                                                name=name,
                                                maxMemoryCapacity=maxMemoryCapacity,
                                                maxVDiskCapacity=maxVDiskCapacity,
                                                maxCPUCapacity=maxCPUCapacity,
                                                maxNASCapacity=maxNASCapacity,
                                                maxNetworkOptTransfer=maxNetworkOptTransfer,
                                                maxNetworkPeerTransfer=maxNetworkPeerTransfer,
                                                maxNumPublicIP=maxNumPublicIP)
            return self.account_get(name, False)

    @property
    def login(self):
        return self._login

    def __repr__(self):
        return "OpenvCloud client: %s" % self._url

    __str__ = __repr__


class Authorizables:

    @property
    def owners(self):
        _owners = []
        for user in self.model['acl']:
            if not user['canBeDeleted']:
                _owners.append(user['userGroupId'])
        return _owners

    @property
    def authorized_users(self):
        return [u['userGroupId'] for u in self.model['acl']]

    def authorize_user(self, username, right=""):
        if not right:
            right = 'ACDRUX'
        if username not in self.authorized_users:
            self._addUser(username, right)
            self.refresh()
        return True

    def unauthorize_user(self, username):
        canBeDeleted = [u['userGroupId']
                        for u in self.model['acl'] if u.get('canBeDeleted', True) is True]
        if username in self.authorized_users and username in canBeDeleted:
            self._deleteUser(username)
            self.refresh()
        return True

    def update_access(self, username, right=""):
        if not right:
            right = 'ACDRUX'
        if username in self.authorized_users:
            self._updateUser(username, right)
            self.refresh()
        return True


class Account(Authorizables):

    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.id = model['id']

    @property
    def spaces(self):
        ovc_spaces = self.client.api.cloudapi.cloudspaces.list()
        spaces = list()
        for space in ovc_spaces:
            if space['accountId'] == self.model['id']:
                spaces.append(Space(self, space))
        return spaces

    @property
    def disks(self):
        """
        Wrapper to list all disks related to an account
        : return: list of disks details
        """
        return self.client.api.cloudapi.disks.list(accountId=self.id)

    def disk_delete(self, disk_id, detach=True):
        """
        Wrapper to delete disk by its id. I think there should be a class for disks to list all its wrappers
        : param disk_id: integer: The disk id need to be removed
        : param detach: boolean: detach the disk from the machine first
        : return:
        """
        return self.client.api.cloudapi.disks.delete(diskId=disk_id, detach=detach)

    def space_get(self, name, location="", create=True,
                  maxMemoryCapacity=-1, maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNASCapacity=-1,
                  maxNetworkOptTransfer=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1,
                  externalnetworkId=None):
        """
        Returns the cloud space with the given name, and in case it doesn't exist yet the account will be created.

        Args:
            - name (required): name of the cloud space to lookup or create if it doesn't exist yet, e.g. "myvdc"
            - location (only required when cloud space needs to be created): location when the cloud space needs to be created
            - create (defaults to True): if set to True the account is created in case it doesn't exist yet
            - maxMemoryCapacity (defaults to -1: unlimited): available memory in GB for all virtual machines in the cloud space
            - maxVDiskCapacity (defaults to -1: unlimited): available disk capacity in GiB for all virtual disks in the cloud space
            - maxCPUCapacity (defaults to -1: unlimited): total number of available virtual CPU core that can be used by the virtual machines in the cloud space
            - maxNASCapacity (defaults to -1: unlimited): not implemented
            - maxNetworkOptTransfer (defaults to -1: unlimited): not implemented
            - maxNetworkPeerTransfer (defaults to -1: unlimited): not implemented
            - maxNumPublicIP (defaults to -1: unlimited): number of external IP addresses that can be used in the cloud space

        Raises:
            - RuntimeError is no location was specified
            - RuntimeError if cloud space doesn't exist, and create argument was set to False
        """
        if not location:
            raise j.exceptions.RuntimeError("Location cannot be empty.")
        for space in self.spaces:
            if space.model['name'] == name and space.model['location'] == location:
                return space
        else:
            if create:
                self.client.api.cloudapi.cloudspaces.create(access=self.client.login,
                                                            name=name,
                                                            accountId=self.id,
                                                            location=location,
                                                            maxMemoryCapacity=maxMemoryCapacity,
                                                            maxVDiskCapacity=maxVDiskCapacity,
                                                            maxCPUCapacity=maxCPUCapacity,
                                                            maxNASCapacity=maxNASCapacity,
                                                            maxNetworkOptTransfer=maxNetworkOptTransfer,
                                                            maxNetworkPeerTransfer=maxNetworkPeerTransfer,
                                                            maxNumPublicIP=maxNumPublicIP,
                                                            externalnetworkId=externalnetworkId)
                return self.space_get(name, location, False)
            else:
                raise j.exceptions.RuntimeError(
                    "Could not find space with name %s" % name)

    def disk_create(self, name, gid, description, size=0, type="B", ssd_size=0):
        res = self.client.api.cloudapi.disks.create(accountId=self.id,
                                                    name=name,
                                                    gid=gid,
                                                    description=description,
                                                    size=size,
                                                    type=type,
                                                    ssdSize=ssd_size)
        return res

    def _addUser(self, username, right):
        self.client.api.cloudapi.accounts.addUser(
            accountId=self.id, userId=username, accesstype=right)

    def _updateUser(self, username, right):
        self.client.api.cloudapi.accounts.updateUser(
            accountId=self.id, userId=username, accesstype=right)

    def _deleteUser(self, username):
        self.client.api.cloudapi.accounts.deleteUser(
            accountId=self.id, userId=username, recursivedelete=True)

    def get_consumption(self, start, end):
        return self.client.api.cloudapi.accounts.getConsumption(accountId=self.id, start=start, end=end)

    def save(self):
        self.client.api.cloudapi.accounts.update(accountId=self.model['id'],
                                                 name=self.model['name'],
                                                 maxMemoryCapacity=self.model.get(
                                                     'maxMemoryCapacity'),
                                                 maxVDiskCapacity=self.model.get(
                                                     'maxVDiskCapacity'),
                                                 maxCPUCapacity=self.model.get(
                                                     'maxCPUCapacity'),
                                                 maxNASCapacity=self.model.get(
                                                     'maxNASCapacity'),
                                                 maxNetworkOptTransfer=self.model.get(
                                                     'maxNetworkOptTransfer'),
                                                 maxNetworkPeerTransfer=self.model.get(
                                                     'maxNetworkPeerTransfer'),
                                                 maxNumPublicIP=self.model.get(
                                                     'maxNumPublicIP')
                                                 )

    def refresh(self):
        accounts = self.client.api.cloudapi.accounts.list()
        found = False
        for account in accounts:
            if account['id'] == self.id:
                self.model = account
                found = True
                break
        if not found:
            raise j.exceptions.RuntimeError("No account found with name %s. The user doesn't have access to the account or it is been deleted." % self.model['name'])

    def delete(self):
        self.client.api.cloudbroker.account.delete(
            accountId=self.id, reason='API request')

    def __str__(self):
        return "OpenvCloud client account: %(name)s" % (self.model)

    __repr__ = __str__


class Space(Authorizables):

    def __init__(self, account, model):
        self.account = account
        self.client = account.client
        self.model = model
        self.id = model["id"]

    def externalnetwork_add(self, name, subnet, gateway, startip, endip, gid, vlan):
        self.client.api.cloudbroker.iaas.addExternalNetwork(cloudspaceId=self.id,
                                                            name=name,
                                                            subnet=subnet,
                                                            getway=gateway,
                                                            startip=startip,
                                                            endip=endip,
                                                            gid=gid,
                                                            vlan=vlan)

    def save(self):
        self.client.api.cloudapi.cloudspaces.update(cloudspaceId=self.model['id'],
                                                    name=self.model['name'],
                                                    maxMemoryCapacity=self.model.get(
                                                        'maxMemoryCapacity'),
                                                    maxVDiskCapacity=self.model.get(
                                                        'maxVDiskCapacity'),
                                                    maxCPUCapacity=self.model.get(
                                                        'maxCPUCapacity'),
                                                    maxNASCapacity=self.model.get(
                                                        'maxNASCapacity'),
                                                    maxNetworkOptTransfer=self.model.get(
                                                        'maxNetworkOptTransfer'),
                                                    maxNetworkPeerTransfer=self.model.get(
                                                        'maxNetworkPeerTransfer'),
                                                    maxNumPublicIP=self.model.get(
                                                        'maxNumPublicIP')
                                                    )

    @property
    def machines(self):
        ovc_machines = self.client.api.cloudapi.machines.list(
            cloudspaceId=self.id)
        machines = dict()
        for machine in ovc_machines:
            machines[machine['name']] = Machine(self, machine)
        return machines

    def _addUser(self, username, right):
        self.client.api.cloudapi.cloudspaces.addUser(
            cloudspaceId=self.id, userId=username, accesstype=right)

    def _deleteUser(self, username):
        self.client.api.cloudapi.cloudspaces.deleteUser(
            cloudspaceId=self.id, userId=username, recursivedelete=True)

    def _updateUser(self, username, right):
        self.client.api.cloudapi.cloudspaces.updateUser(
            cloudspaceId=self.id, userId=username, accesstype=right)

    def enable(self, reason):
        """
        Will enable the cloud space.
        : param reason: string: The reason why the cloud space should be enabled.
        """
        self.client.api.cloudapi.cloudspaces.enable(
            cloudspaceId=self.id, reason=reason)

    def disable(self, reason):
        """
        Will disable the cloud space.
        : param reason: string: The reason why the cloud space should be disabled.
        """
        self.client.api.cloudapi.cloudspaces.disable(
            cloudspaceId=self.id, reason=reason)

    def refresh(self):
        cloudspaces = self.client.api.cloudapi.cloudspaces.list()
        for cloudspace in cloudspaces:
            if cloudspace['id'] == self.id:
                self.model = cloudspace
                break
        else:
            raise j.exceptions.RuntimeError("Cloud space has been deleted")

    def machine_get(
            self,
            name,
            create=False,
            sshkeyname="",
            memsize=2,
            vcpus=1,
            disksize=10,
            datadisks=[],
            image="Ubuntu 16.04 x64",
            sizeId=None,
            stackId=None):
        """
        Returns the virtual machine with given name, and in case it doesn't exist yet creates the machine if the create argument is set to True.

        Args:
            - name: (required) name of the virtual machine to lookup or create if it doesn't exist yet, e.g. "My first VM"
            - create (defaults to False): if set to true the machine is created in case it doesn't exist yet
            - sshkeyname (only required for creating new machine): name of the private key loaded by ssh-agent that will get copied into authorized_keys
            - memsize (defaults to 2): memory size in MB or in GB, e.g. 4096
            - vcpus (defaults to 1): number of virtual CPU cores; value is ignored in versions prior to 3.x, use sizeId in order to set the number of virtual CPU cores
            - disksize (default to 10): boot disk size in MB
            - datadisks (optional): list of data disks sizes in GB, e.g. [20, 20, 50]
            - image (defaults to "Ubuntu 16.04 x6"): name of the OS image to load
            - sizeId (optional): overrides the value set for memsize, denotes the type or "size" of the virtual machine, actually sets the number of virtual CPU cores and amount of memory, see the sizes property of the cloud space for the sizes available in the cloud space
            - stackId (optional): identifies the grid node on which to create the virtual machine, if nothing specified (recommended) OpenvCloud will decide where to create the virtual machine

        Raises: RuntimeError if machine doesn't exist, and create argument was set to False (default)
        """
        machines = self.machines
        if name not in machines:
            if create == True:
                return self.machine_create(name=name,
                                           sshkeyname=sshkeyname,
                                           memsize=memsize,
                                           vcpus=vcpus,
                                           disksize=disksize,
                                           datadisks=datadisks,
                                           image=image,
                                           sizeId=sizeId,
                                           stackId=stackId)
            else:
                raise RuntimeError("Cannot find machine:%s" % name)
        else:
            return machines[name]

    def machines_delete(self):
        """
        Deletes all machines in the cloud space.
        """
        for key, machine in self.machines.items():
            machine.delete()

    def machine_create(
            self,
            name,
            sshkeyname=None,
            memsize=2,
            vcpus=None,
            disksize=10,
            datadisks=[],
            image="Ubuntu 16.04 x64",
            sizeId=None,
            stackId=None,
            sshkeypath=None,
            ignore_name_exists = False
    ):
        """
        Creates a new virtual machine if a one with the same name does not exist.

        Args:
            - name (required): name of the virtual machine, e.g. "My first VM"
            - sshkeyname (required): name of the private key loaded by ssh-agent that will get copied into authorized_keys
            - memsize (defaults to 2): memory size in MB or in GB, e.g. 4096
            - vcpus (defaults to 1): number of virtual CPU cores; value is ignored in versions prior to 3.x, use sizeId in order to set the number of virtual CPU cores
            - disksize (default to 10): boot disk size in MB
            - datadisks (optional): list of data disks sizes in GB, e.g. [20, 20, 50]
            - image (defaults to "Ubuntu 16.04 x6"): name of the OS image to load
            - sizeId (optional): overrides the value set for memsize, denotes the type or "size" of the virtual machine, actually sets the number of virtual CPU cores and amount of memory, see the sizes property of the cloud space for the sizes available in the cloud space
            - stackId (optional): identifies the grid node on which to create the virtual machine, if nothing specified (recommended) OpenvCloud will decide where to create the virtual machine
            - sshkeypath (optional): if not None the sshkey will be reloaded before getting a prefab
            - ignore_name_exists (Optional): When set to True will not raise RuntimeError when the name already exist
        Raises:
            - RuntimeError if machine with given name already exists and ignore_name_exists is False.
            - RuntimeError if machine name contains spaces
        """
        if ' ' in name:
            raise RuntimeError('Name cannot contain spaces')
        imageId = self.image_find_id(image)
        if sizeId is None:
            sizeId = self.size_find_id(memsize, vcpus)
        if name in self.machines and not ignore_name_exists:
            raise j.exceptions.RuntimeError(
                "Name is not unique, already exists in %s" % self)
        print("Cloud space ID:%s name:%s size:%s image:%s disksize:%s" %
              (self.id, name, sizeId, imageId, disksize))

        machine = self.machines.get(name)
        if not machine:
            if stackId:
                self.client.api.cloudbroker.machine.createOnStack(
                    cloudspaceId=self.id,
                    name=name,
                    sizeId=sizeId,
                    imageId=imageId,
                    disksize=disksize,
                    datadisks=datadisks,
                    stackid=stackId)
            else:
                res = self.client.api.cloudapi.machines.create(
                    cloudspaceId=self.id, name=name, sizeId=sizeId, imageId=imageId, disksize=disksize, datadisks=datadisks)

        print("machine created.")
        machine = self.machines[name]

        self.configure_machine(machine=machine, name=name, sshkey_name=sshkeyname, sshkey_path=sshkeypath)

        return machine

    def configure_machine(self, machine, name, sshkey_name, sshkey_path):
        self.createPortForward(machine)

        self._authorizeSSH(machine=machine, sshkey_name=sshkey_name, sshkey_path=sshkey_path)

        prefab = machine.prefab
        prefab.core.hostname = name  # make sure hostname is set

        # remember the node in the local node configuration
        j.tools.develop.nodes.nodeSet(name, addr=prefab.executor.sshclient.addr,
                                      port=prefab.executor.sshclient.port,
                                      cat="openvcloud", description="deployment in openvcloud")

    def createPortForward(self, machine):
        machineip, _ = machine.machineip_get()
        sshport = None
        usedports = set()
        for portforward in machine.space.portforwards:
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                break
            usedports.add(int(portforward['publicPort']))

        if sshport is None:
            requested_sshport = 2200
            while requested_sshport in usedports:
                requested_sshport += 1
            machine.portforward_create(requested_sshport, 22)
            sshport = requested_sshport
        return sshport;

    def _getPortForward(self, machine):
        machineip, _ = machine.machineip_get()
        sshport = None
        for portforward in machine.space.portforwards:
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                break
        return sshport

    def _authorizeSSH(self, machine, sshkey_name, sshkey_path):
        print("authorize ssh")

        # prepare data required for sshclient
        machineip, machinedict = machine.machineip_get()
        publicip = machine.space.model['publicipaddress']
        sshport = self._getPortForward(machine)
        if sshport == None:
            sshport = self.createPortForward(machine)
        login = machinedict['accounts'][0]['login']
        password = machinedict['accounts'][0]['password']

        # make sure that SSH key is loaded
        sshclient = j.clients.ssh.get(
            addr=publicip, port=sshport, login=login, passwd=password, look_for_keys=False, timeout=300)
        sshclient.SSHAuthorizeKey(sshkey_name, sshkey_path)

        machine.ssh_keypath = sshkey_path
        return machine.prefab

    @property
    def portforwards(self):
        return self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.id)

    def portforward_exists(self, publicIp, publicport, protocol):
        for pf in self.portforwards:
            if pf['publicIp'] == publicIp and int(pf['publicPort']) == int(publicport) and pf['protocol'] == protocol:
                return True
        return False

    def size_find_id(self, memory=None, vcpus=None):
        if memory < 100:
            memory = memory * 1024  # prob given in GB

        sizes = [(item["memory"], item) for item in self.sizes]
        sizes.sort(key=lambda size: size[0], reverse=True)
        for size, sizeinfo in sizes:
            if memory > size / 1.1:
                if vcpus and vcpus != sizeinfo['vcpus']:
                    continue
                return sizeinfo['id']

        raise j.exceptions.RuntimeError("did not find memory size:%s, or found with different vcpus" % memory)

    @property
    def sizes(self):
        return self.client.api.cloudapi.sizes.list(cloudspaceId=self.id)

    def image_find_id(self, name):
        name = name.lower()

        for image in self.images:
            imageNameFound = image["name"].lower()
            if imageNameFound.find(name) != -1:
                return image["id"]
        images = [item["name"].lower() for item in self.images]
        raise j.exceptions.RuntimeError(
            "did not find image:%s\nPossible Images:\n%s\n" % (name, images))

    @property
    def images(self):
        return self.client.api.cloudapi.images.list(cloudspaceId=self.id, accountId=self.account.id)

    def delete(self):
        self.client.api.cloudapi.cloudspaces.delete(cloudspaceId=self.id)

    def execute_routeros_script(self, script):
        self.client.api.cloudapi.cloudspaces.executeRouterOSScript(
            cloudspaceId=self.id, script=script)

    def get_space_ip(self):
        space = self.client.api.cloudapi.cloudspaces.get(cloudspaceId=self.id)

        def getSpaceIP(space):
            if space['publicipaddress'] == '':
                space = self.client.api.cloudapi.cloudspaces.get(
                    cloudspaceId=self.id)
            return space['publicipaddress']

        space_ip = getSpaceIP(space)
        start = time.time()
        timeout = 120
        while space_ip == '' and start + timeout > time.time():
            time.sleep(5)
            space_ip = getSpaceIP(space)
        if space_ip == '':
            raise j.exceptions.RuntimeError(
                "Could not get IP Address for space %(name)s" % space)
        return space_ip

    def __repr__(self):
        return "space: %s (%s)" % (self.model["name"], self.id)

    __str__ = __repr__


class Machine:

    def __init__(self, space, model):
        self.space = space
        self.client = space.client
        self.model = model
        self._prefab = None
        self.id = self.model["id"]
        self.name = self.model["name"]
        self.ssh_keypath = None

    def start(self):
        self.client.api.cloudapi.machines.start(machineId=self.id)

    def stop(self):
        self.client.api.cloudapi.machines.stop(machineId=self.id)

    def restart(self):
        self.client.api.cloudapi.machines.reboot(machineId=self.id)

    def pause(self):
        self.client.api.cloudapi.machines.pause(machineId=self.id)

    def resume(self):
        self.client.api.cloudapi.machines.resume(machineId=self.id)

    def reset(self):
        self.client.api.cloudapi.machines.reset(machineId=self.id)

    def delete(self):
        print("Machine delete:%s" % self)
        self.client.api.cloudapi.machines.delete(machineId=self.id)

    def clone(self, name, cloudspaceId=None, snapshotTimestamp=None):
        """
        Will create a new machine that is a clone of this one.
        : param name: the name of the clone that will be created.
        : param cloudspaceId: optional id of the cloud space in which the machine should be put.
        : param snapshotTimestamp: optional snapshot to base the clone upon.
        : return: the id of the created machine
        """
        return self.client.api.cloudapi.machines.clone(machineId=self.id,
                                                       name=name,
                                                       cloudspaceId=cloudspaceId,
                                                       snapshotTimestamp=snapshotTimestamp)

    def snapshot_create(self, name=None):
        """
        Will create a snapshot of the machine.
        : param name: the name of the snapshot that will be created. Default: creation time
        """
        if name is None:
            name = str(datetime.datetime.now())
        self.client.api.cloudapi.machines.snapshot(
            machineId=self.id, name=name)

    @property
    def snapshots(self):
        """
        Will return a list of snapshots of the machine.
        : return: the list of snapshots
        """
        return self.client.api.cloudapi.machines.listSnapshots(machineId=self.id)

    def snapshot_delete(self, epoch):
        """
        Will delete a snapshot of the machine.
        : param epoch: the epoch of the snapshot to be deleted.
        """
        self.client.api.cloudapi.machines.deleteSnapshot(
            machineId=self.id, epoch=epoch)

    def snapshot_rollback(self, epoch):
        """
        Will rollback a snapshot of the machine.
        : param epoch: the epoch of the snapshot to be rollbacked.
        """
        self.client.api.cloudapi.machines.rollbackSnapshot(
            machineId=self.id, epoch=epoch)

    def history_get(self, size):
        return self.client.api.cloudapi.machines.getHistory(machineId=self.id, size=size)

    def externalnetwork_attach(self):
        self.client.api.cloudapi.machines.attachExternalNetwork(
            machineId=self.id)

    def externalnetwork_detach(self):
        self.client.api.cloudapi.machines.detachExternalNetwork(
            machineId=self.id)

    def disk_add(self, name, description, size=10, type='D', ssdSize=0):
        disk_id = self.client.api.cloudapi.machines.addDisk(machineId=self.id,
                                                            diskName=name,
                                                            description=description,
                                                            size=size,
                                                            type=type,
                                                            ssdSize=ssdSize)
        return disk_id

    @property
    def disks(self):
        """
        Wrapper to list all disks related to a machine
        : return: list of disks details
        """
        machine_data = self.client.api.cloudapi.machines.get(machineId=self.id)
        return [disk for disk in machine_data['disks'] if disk['type'] != 'M']

    def disk_detach(self, disk_id):
        return self.client.api.cloudapi.machines.detachDisk(machineId=self.id, diskId=disk_id)

    def disk_limit_io(self, disk_id, total_bytes_sec, read_bytes_sec, write_bytes_sec, total_iops_sec,
                      read_iops_sec, write_iops_sec, total_bytes_sec_max, read_bytes_sec_max,
                      write_bytes_sec_max, total_iops_sec_max, read_iops_sec_max,
                      write_iops_sec_max, size_iops_sec, iops=50):
        self.client.api.cloudapi.disks.limitIO(diskId=disk_id, iops=iops, total_bytes_sec=total_bytes_sec,
                                               read_bytes_sec=read_bytes_sec,
                                               write_bytes_sec=write_bytes_sec, total_iops_sec=total_iops_sec,
                                               read_iops_sec=read_iops_sec, write_iops_sec=write_iops_sec,
                                               total_bytes_sec_max=total_bytes_sec_max, read_bytes_sec_max=read_bytes_sec_max,
                                               write_bytes_sec_max=write_bytes_sec_max, total_iops_sec_max=total_iops_sec_max,
                                               read_iops_sec_max=read_iops_sec_max, write_iops_sec_max=write_iops_sec_max,
                                               size_iops_sec=size_iops_sec)

    @property
    def portforwards(self):
        return self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.space.id, machineId=self.id)

    def portforward_create(self, publicport, localport, protocol='tcp'):
        if protocol not in ['tcp', 'udp']:
            raise j.exceptions.RuntimeError(
                "Protocol for portforward should be tcp or udp not %s" % protocol)

        machineip, _ = self.machineip_get()

        publicAddress = self.space.model['publicipaddress']
        if not publicAddress:
            raise j.exceptions.RuntimeError(
                "No public address found, cannot create port forward")

        # define real publicport, override it by a generated one if needed
        realpublicport = publicport

        if publicport is None:
            unavailable_ports = [int(portinfo['publicPort'])
                                 for portinfo in self.space.portforwards]
            candidate = 2200

            while candidate in unavailable_ports:
                candidate += 1

            realpublicport = candidate

        try:
            self.client.api.cloudapi.portforwarding.create(
                cloudspaceId=self.space.id,
                protocol=protocol,
                localPort=localport,
                machineId=self.id,
                publicIp=publicAddress,
                publicPort=realpublicport
            )

        except Exception as e:
            # if we have a conflict response, let's check something:
            # - if it's an auto-generated port, we probably hit a concurrence issue
            #   let's try again with a new port
            if str(e).startswith("409 Conflict") and publicport is None:
                return self.portforward_create(None, localport, protocol)

            # - if the port was choose explicitly, then it's not the lib's fault
            raise j.exceptions.RuntimeError(
                "Port forward already exists. Please specify another port forwarding")

        return (realpublicport, localport)

    def portforward_delete(self, publicport):
        self.client.api.cloudapi.portforwarding.deleteByPort(
            cloudspaceId=self.space.id,
            publicIp=self.space.model['publicipaddress'],
            publicPort=publicport,
            proto='tcp'
        )

    def portforward_delete_by_id(self, pfid):
        self.client.api.cloudapi.portforwarding.delete(cloudspaceid=self.space.id,
                                                       id=pfid)

    def machineip_get(self):
        machine = self.client.api.cloudapi.machines.get(machineId=self.id)

        def getMachineIP(machine):
            if machine['interfaces'][0]['ipAddress'] == 'Undefined':
                machine = self.client.api.cloudapi.machines.get(
                    machineId=self.id)
            return machine['interfaces'][0]['ipAddress']

        machineip = getMachineIP(machine)
        start = time.time()
        timeout = 200
        while machineip == 'Undefined' and start + timeout > time.time():
            time.sleep(5)
            machineip = getMachineIP(machine)
        if machineip == 'Undefined':
            raise j.exceptions.RuntimeError(
                "Could not get IP Address for machine %(name)s" % machine)
        return machineip, machine

    @property
    def prefab(self):
        """
        Will get a prefab executor for the machine.
        Will attempt to create a portforwarding

        the sshkeyname needs to be loaded in local ssh-agent (this is the only supported method!)

        login/passwd has been made obsolete, its too dangerous

        """
        if self._prefab is None:
            machineip, machine = self.machineip_get()
            publicip = self.space.model['publicipaddress']
            while not publicip:
                time.sleep(5)
                self.space.refresh()
                publicip = self.space.model['publicipaddress']

            sshport = None
            usedports = set()
            for portforward in self.space.portforwards:
                if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                    sshport = int(portforward['publicPort'])
                    break
                usedports.add(int(portforward['publicPort']))

            if sshport is None:
                raise RuntimeError(
                    "Cannot find sshport at public side to access this machine")

            #load SSH key if a ssh_keypath provided to the machine
            executor = None
            if self.ssh_keypath:
                j.clients.ssh.load_ssh_key(self.ssh_keypath)
                sshclient = j.clients.ssh.get(addr=publicip, port=sshport, key_filename=self.ssh_keypath)
                sshclient._connect()
                executor = j.tools.executor.getFromSSHClient(sshclient)
            else:
                sshclient = j.clients.ssh.get(addr=publicip, port=sshport)
                executor = j.tools.executor.getFromSSHClient(sshclient)
            
    
            self._prefab = j.tools.prefab.get(executor, usecache=False)

        return self._prefab

    def __repr__(self):
        return "machine: %s (%s)" % (self.model["name"], self.id)

    __str__ = __repr__
