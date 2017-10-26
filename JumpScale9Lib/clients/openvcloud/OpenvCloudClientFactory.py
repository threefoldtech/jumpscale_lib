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
        j.do.execute("pip3 install python-jose")

    def _urlClean(self, url):
        url = url.lower()
        if url.startswith("http"):
            url = url.split("//")[1].rstrip("/")
        print("get openvcloud client on url:%s" % url)
        return url

    def getLegacy(self, url, login=None, password=None):
        """

        only use this for legacy reasons or private deployments where there is no itsyou.online used

        if you want to use secret or jwt, DO not use this method use .getFromApiSecret(...)

        url e.g. https://se-gen-1.demo.greenitglobe.com/  (is the base url of the environment)


        """
        url = self._urlClean(url)
        cl = Client(url, login, password, secret=None, port=443, jwt=None)
        return cl

    def getFromAYSService(self, service):
        """
        start from an atyourservice service
        """
        return self.get(
            url=service.model.data.url,
            login=service.model.data.login,
            password=service.model.data.password,
            jwt=service.model.data.jwt,
            port=service.model.data.port)

    def get(self, applicationId, secret, url):
        """
        this is the default way how to do this, create a secret/app key on ityou.online

        instructions see: 

        url e.g. https://se-gen-1.demo.greenitglobe.com/  (is the base url of the environment)        
        """
        url = self._urlClean(url)
        jwt = self.getJWTTokenFromItsYouOnline(applicationId, secret)
        login = None
        password = None
        port = 443
        cl = Client(url, login, password, secret, port, jwt)
        return cl

    def getJWTTokenFromItsYouOnline(self, applicationId, secret, validity=3600):
        """
        this method will return jwt token starting from applicationId & secret

        go to https: // itsyou.online/  # /settings add api key (label is not important)

        get the appid & secret from there

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
                "Can not connect to openvcloud without either password, secret or jwt")
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
                "Can not connect to openvcloud without either password, secret or jwt")
        if jwt:
            import jose.jwt
            payload = jose.jwt.get_unverified_claims(jwt)
            if payload['exp'] < time.time():
                jwt = refresh_jwt(jwt, payload)
            self.api._session.headers['Authorization'] = 'bearer {}'.format(
                jwt)
            self._login = payload['username']
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
        return "openvcloud client: %s" % self._url

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

    def delete_disk(self, disk_id, detach=True):
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
        will get space if it exists, if not will create it
        to retrieve existing one location does not have to be specified

        example: for ms1 possible locations: ca1, eu1(uk), eu2(be)

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

    @property
    def disks(self):
        """
        Wrapper to list all disks related to an account
        : return: dict list of disks details
        """
        return self.client.api.cloudapi.disks.list(accountId=self.id)

    def delete_disk(self, disk_id, detach=True):
        """
        Wrapper to delete disk by its id. I think there should be a class for disks to list all its wrappers
        : param disk_id: integer: The disk id need to be removed
        : param detach: boolean: detach the disk from the machine first
        : return:
        """
        return self.client.api.cloudapi.disks.delete(diskId=disk_id, detach=detach)

    def create_disk(self, name, gid, description, size=0, type="B", ssd_size=0):
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
        for account in accounts:
            if account['id'] == self.id:
                self.model = account
                break
        else:
            raise j.exceptions.RuntimeError("Account has been deleted")

    def delete(self):
        self.client.api.cloudbroker.account.delete(
            accountId=self.id, reason='API request')

    def __str__(self):
        return "openvcloud client account: %(name)s" % (self.model)

    __repr__ = __str__


class Space(Authorizables):

    def __init__(self, account, model):
        self.account = account
        self.client = account.client
        self.model = model
        self.id = model["id"]

    def add_external_network(self, name, subnet, gateway, startip, endip, gid, vlan):
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
        Will enable the cloudspace.
        : param reason: string: The reason why the cloudspace should be enabled.
        """
        self.client.api.cloudapi.cloudspaces.enable(
            cloudspaceId=self.id, reason=reason)

    def disable(self, reason):
        """
        Will disable the cloudspace.
        : param reason: string: The reason why the cloudspace should be disabled.
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
            raise j.exceptions.RuntimeError("Cloudspace has been deleted")

    def machine_create_ifnotexist(
            self,
            name,
            sshkeyname,
            memsize=2,
            vcpus=1,
            disksize=10,
            datadisks=[],
            image="Ubuntu 16.04 x64",
            sizeId=None,
            stackId=None):
        """
        @param memsize in MB or GB
        for now vcpu's is ignored(waiting for openvcloud)


        """
        machines = self.machines
        if name not in machines:
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
            return machines[name]

    def machine_get(self, name):
        machines = self.machines
        if name not in machines:
            raise RuntimeError("Cannot find machine:%s" % name)
        else:
            return machines[name]

    def machines_delete(self):
        for key, machine in self.machines.items():
            machine.delete()

    def machine_create(
            self,
            name,
            sshkeyname,
            memsize=2,
            vcpus=1,
            disksize=10,
            datadisks=[],
            image="Ubuntu 16.04 x64",
            sizeId=None,
            stackId=None,
    ):
        """
        @param sshkeyname is obliged will get key from ssh-agent and needs to be loaded !!!

        @param memsize in MB or GB
        for now vcpu's is ignored(waiting for openvcloud)

        """
        imageId = self.image_find_id(image)
        if sizeId is None:
            sizeId = self.size_find_id(memsize)
        if name in self.machines:
            raise j.exceptions.RuntimeError(
                "Name is not unique, already exists in %s" % self)
        print("cloudspaceid:%s name:%s size:%s image:%s disksize:%s" %
              (self.id, name, sizeId, imageId, disksize))
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
            print("created machine")
            machine = self.machines[name]
            self._authorizeSSH(machine, sshkeyname=sshkeyname)

        m = self.machines[name]
        p = m.prefab
        p.core.hostname = name  # make sure hostname is set

        # remember the node in the local node configuration
        j.tools.develop.nodes.nodeSet(name, addr=p.executor.sshclient.addr, port=p.executor.sshclient.port,
                                      cat="openvcloud", description="deployment in openvcloud")

        return m

    def _authorizeSSH(self, machine, sshkeyname):
        print("authorize ssh")
        machineip, machinedict = machine.get_machine_ip()
        publicip = machine.space.model['publicipaddress']
        while not publicip:
            print(
                "machine openvcloud:%s not ready yet with public ip, wait 1 sec, try again" % self)
            time.sleep(1)
            machine.space.refresh()
            publicip = machine.space.model['publicipaddress']

        sshport = None
        usedports = set()
        for portforward in machine.space.portforwardings:
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                break
            usedports.add(int(portforward['publicPort']))

        if sshport is None:
            requested_sshport = 2200
            while requested_sshport in usedports:
                requested_sshport += 1
            machine.create_portforwarding(requested_sshport, 22)

            sshport = requested_sshport

        login = machinedict['accounts'][0]['login']
        password = machinedict['accounts'][0]['password']

        sshclient = j.clients.ssh.get(
            addr=publicip, port=sshport, login=login, passwd=password, look_for_keys=False, timeout=5)
        sshclient.SSHAuthorizeKey(sshkeyname)

    @property
    def portforwardings(self):
        return self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.id)

    def isPortforwardExists(self, publicIp, publicport, protocol):
        for pf in self.portforwardings:
            if pf['publicIp'] == publicIp and int(pf['publicPort']) == int(publicport) and pf['protocol'] == protocol:
                return True
        return False

    def size_find_id(self, memory=None, vcpus=None):
        if memory < 100:
            memory = memory * 1024  # prob given in GB

        sizes = [(item["memory"], item) for item in self.sizes]
        sizes.sort(key=lambda size: size[0])
        sizes.reverse()
        for size, sizeinfo in sizes:
            if memory > size / 1.1:
                return sizeinfo['id']

        raise j.exceptions.RuntimeError("did not find memory size:%s" % memory)

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
        : param cloudspaceId: optional id of the cloudspace in which the machine should be put.
        : param snapshotTimestamp: optional snapshot to base the clone upon.
        : return: the id of the created machine
        """
        return self.client.api.cloudapi.machines.clone(machineId=self.id,
                                                       name=name,
                                                       cloudspaceId=cloudspaceId,
                                                       snapshotTimestamp=snapshotTimestamp)

    def create_snapshot(self, name=None):
        """
        Will create a snapshot of the machine.
        : param name: the name of the snapshot that will be created. Default: creation time
        """
        if name is None:
            name = str(datetime.datetime.now())
        self.client.api.cloudapi.machines.snapshot(
            machineId=self.id, name=name)

    def list_snapshots(self):
        """
        Will return a list of snapshots of the machine.
        : return: the list of snapshots
        """
        return self.client.api.cloudapi.machines.listSnapshots(machineId=self.id)

    def delete_snapshot(self, epoch):
        """
        Will delete a snapshot of the machine.
        : param epoch: the epoch of the snapshot to be deleted.
        """
        self.client.api.cloudapi.machines.deleteSnapshot(
            machineId=self.id, epoch=epoch)

    def rollback_snapshot(self, epoch):
        """
        Will rollback a snapshot of the machine.
        : param epoch: the epoch of the snapshot to be rollbacked.
        """
        self.client.api.cloudapi.machines.rollbackSnapshot(
            machineId=self.id, epoch=epoch)

    def getHistory(self, size):
        return self.client.api.cloudapi.machines.getHistory(machineId=self.id, size=size)

    def attach_external_network(self):
        self.client.api.cloudapi.machines.attachExternalNetwork(
            machineId=self.id)

    def detach_external_network(self):
        self.client.api.cloudapi.machines.detachExternalNetwork(
            machineId=self.id)

    def add_disk(self, name, description, size=10, type='D', ssdSize=0):
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
        return machine_data['disks']

    def detach_disk(self, disk_id):
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
    def portforwardings(self):
        return self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.space.id, machineId=self.id)

    def create_portforwarding(self, publicport, localport, protocol='tcp'):
        if protocol not in ['tcp', 'udp']:
            raise j.exceptions.RuntimeError(
                "Protocol for portforward should be tcp or udp not %s" % protocol)

        machineip, _ = self.get_machine_ip()

        publicAddress = self.space.model['publicipaddress']
        if not publicAddress:
            raise j.exceptions.RuntimeError(
                "No public address found, cannot create port forward")

        # define real publicport, override it by a generated one if needed
        realpublicport = publicport

        if publicport is None:
            unavailable_ports = [int(portinfo['publicPort'])
                                 for portinfo in self.space.portforwardings]
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
                return self.create_portforwarding(None, localport, protocol)

            # - if the port was choose excplicitly, then it's not the lib's fault
            raise j.exceptions.RuntimeError(
                "Port forward already exists. Please specify another port forwarding")

        return (realpublicport, localport)

    def delete_portforwarding(self, publicport):
        self.client.api.cloudapi.portforwarding.deleteByPort(
            cloudspaceId=self.space.id,
            publicIp=self.space.model['publicipaddress'],
            publicPort=publicport,
            proto='tcp'
        )

    def delete_portfowarding_by_id(self, pfid):
        self.client.api.cloudapi.portforwarding.delete(cloudspaceid=self.space.id,
                                                       id=pfid)

    def get_machine_ip(self):
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
            machineip, machine = self.get_machine_ip()
            publicip = self.space.model['publicipaddress']
            while not publicip:
                time.sleep(5)
                self.space.refresh()
                publicip = self.space.model['publicipaddress']

            sshport = None
            usedports = set()
            for portforward in self.space.portforwardings:
                if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                    sshport = int(portforward['publicPort'])
                    break
                usedports.add(int(portforward['publicPort']))

            if sshport == None:
                raise RuntimeError(
                    "Cannot find sshport at public side to access this machine")

            sshclient = j.clients.ssh.get(addr=publicip, port=sshport)

            executor = j.tools.executor.getFromSSHClient(sshclient)

            self._prefab = j.tools.prefab.get(executor)

        return self._prefab

    def __repr__(self):
        return "machine: %s (%s)" % (self.model["name"], self.id)

    __str__ = __repr__
