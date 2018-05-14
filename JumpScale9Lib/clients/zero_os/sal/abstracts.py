from js9 import j


class Mountable():
    """
    Abstract implementation for devices that are mountable.
    Device should have attributes devicename and mountpoint
    """

    def mount(self, target, options=['defaults']):
        """
        @param target: Mount point
        @param options: Optional mount options
        """
        if self.mountpoint == target:
            return

        self.client.bash('mkdir -p {}'.format(target))

        self.client.disk.mount(
            source=self.devicename,
            target=target,
            options=options,
        )

        self.mountpoint = target

    def umount(self):
        """
        Unmount disk
        """
        _mount = self.mountpoint
        if _mount:
            self.client.disk.umount(
                source=_mount,
            )
            self.client.bash("rm -rf %s" % _mount).get()
        self.mountpoint = None


class Collection:
    def __init__(self, parent):
        self._parent = parent
        self._items = []

    def __iter__(self):
        for item in self._items:
            yield item

    def __getitem__(self, name):
        if isinstance(name, int):
            return self._items[name]
        for item in self._items:
            if item.name == name:
                return item
        raise KeyError('Name {} does not exists'.format(name))

    def __contains__(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    def add(self, name, *args, **kwargs):
        if name in self:
            raise ValueError('Element with name {} already exists'.format(name))

    def remove(self, item):
        """
        Remove item from collection

        :param item: Item can be the index, the name or the object itself to remove
        :type item: mixed
        """
        if isinstance(item, (str, int)):
            item = self[item]
        self._items.remove(item)

    def list(self):
        return list(self)

    def __str__(self):
        return str(self._items)

    __repr__ = __str__


class Nic:
    def __init__(self, name, type_, networkid, hwaddr, parent):
        self._type = None
        self.name = name
        self.networkid = networkid
        self.type = type_
        self.hwaddr = hwaddr
        self._parent = parent

    def __str__(self):
        return "{} <{}:{}:{}>".format(self.__class__.__name__, self.name, self.type, self.networkid)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in ['vxlan', 'vlan', 'bridge', 'default', 'zerotier']:
            raise ValueError('Invalid nic type {}'.format(value))
        self._type = value

    def to_dict(self, forvm=False, forcontainer=False):
        nicinfo = {
            'id': str(self.networkid),
            'type': self.type,
            'name': self.name
        }
        if forvm:
            nicinfo.pop('name')
        if self.hwaddr:
            nicinfo['hwaddr'] = self.hwaddr
        return nicinfo

    __repr__ = __str__


class ZTNic(Nic):
    def __init__(self, name, networkid, hwaddr, parent):
        super().__init__(name, 'zerotier', networkid, hwaddr, parent)
        self._client = None
        self._client_name = None

    @property
    def client_name(self):
        return self._client_name

    @property
    def client(self):
        if self._client is None and self._client_name:
            self._client = j.clients.zerotier.get(self._client_name, create=False, die=True, interactive=False) 
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @client_name.setter
    def client_name(self, value):
        if value not in j.clients.zerotier.list():
            raise ValueError('There is no zerotier client with name {}'.format(value))
        self._client_name = value
        self.client = j.clients.zerotier.get(value)

    def authorize(self, publicidentity):
        """
        Authorize zerotier network
        """
        if not self.client:
            return False
        network = self.client.network_get(self.networkid)
        network.member_add(publicidentity, self._parent.name)
        return True

    def to_dict(self, forvm=False, forcontainer=False):
        data = super().to_dict(forvm, forcontainer)
        if forcontainer:
            return data

        if self.client:
            data['ztClient'] = self.client.config.instance
        elif self._client_name:
            data['ztClient'] = self._client_name
        return data


class Nics(Collection):
    def add(self, name, type_, networkid=None, hwaddr=None):
        """
        Add nic to VM

        :param name: name to give to the nic
        :type name: str
        :param type_: Nic type vlan, vxlan, zerotier, bridge or default
        :type type_: str
        :param hwaddr: Hardware address of the NIC (MAC)
        :param type: str
        """
        super().add(name)
        if len(name) > 15 or name == 'default':
            raise ValueError('Invalid network name {} should be max 15 chars and not be \'default\''.format(name))
        if networkid is None and type_ != 'default':
            raise ValueError('Missing required argument networkid for type {}'.format(type_))
        if type_ == 'zerotier':
            nic = ZTNic(name, networkid, hwaddr, self._parent)
        else:
            nic = Nic(name, type_, networkid, hwaddr, self._parent)
        self._items.append(nic)
        return nic

    def add_zerotier(self, network, name=None):
        """
        Add zerotier by zerotier network

        :param network: Zerotier network instance (part of zerotierclient)
        :type network: JumpScale9Lib.clients.zerotier.ZerotierClient.ZeroTierNetwork
        :param name: Name for the nic if left blank will be the name of the network
        :type name: str
        """
        name = name or network.name
        nic = ZTNic(name, network.id, None, self._parent)
        nic.client = network.client
        self._items.append(nic)
        return nic

    def get_by_type_id(self, type_, networkid):
        for nic in self:
            if nic.networkid == str(networkid) and nic.type == type_:
                return nic
        raise LookupError('No nic found with type id combination {}:'.format(type_, networkid))


class DynamicCollection:
    def __iter__(self):
        for item in self.list():
            yield item

    def __getitem__(self, name):
        for item in self.list():
            if item.name == name:
                return item
        raise KeyError('Name {} does not exists'.format(name))

    def __contains__(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    def __str__(self):
        return str(self.list())

    __repr__ = __str__

