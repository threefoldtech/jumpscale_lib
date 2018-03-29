import time
from collections import namedtuple
from datetime import datetime
from io import BytesIO

import netaddr
import redis
from js9 import j

from .Capacity import Capacity
from .Container import Containers
from .Disk import Disks, StorageType
from .healthcheck import HealthCheck
from .Network import Network
from .StoragePool import StoragePools
from .gateway import Gateways
from .Hypervisor import Hypervisor

Mount = namedtuple('Mount', ['device', 'mountpoint', 'fstype', 'options'])
logger = j.logger.get(__name__)


class Node:
    """Represent a Zero-OS Server"""

    def __init__(self, client):
        # g8os client to talk to the node
        self._storageAddr = None
        self.addr = client.config.data['host']
        self.port = client.config.data['port']
        self.disks = Disks(self)
        self.storagepools = StoragePools(self)
        self.containers = Containers(self)
        self.gateways = Gateways()
        self.hypervisor = Hypervisor(self)
        self.network = Network(self)
        self.healthcheck = HealthCheck(self)
        self.capacity = Capacity(self)
        self.client = client

    @property
    def name(self):
        def get_nic_hwaddr(nics, name):
            for nic in nics:
                if nic['name'] == name:
                    return nic['hardwareaddr']

        defaultgwdev = self.client.bash("ip route | grep default | awk '{print $5}'", max_time=60).get().stdout.strip()
        nics = self.client.info.nic()
        macgwdev = None
        if defaultgwdev:
            macgwdev = get_nic_hwaddr(nics, defaultgwdev)
        if not macgwdev:
            raise AttributeError("name not find for node {}".format(self))
        return macgwdev.replace(":", '')

    @property
    def storageAddr(self):
        if not self._storageAddr:
            nic_data = self.client.info.nic()
            for nic in nic_data:
                if nic['name'] == 'backplane':
                    for ip in nic['addrs']:
                        network = netaddr.IPNetwork(ip['addr'])
                        if network.version == 4:
                            self._storageAddr = network.ip.format()
                            return self._storageAddr
            self._storageAddr = self.addr
        return self._storageAddr

    def get_nic_by_ip(self, addr):
        try:
            res = next(nic for nic in self.client.info.nic() if any(addr == a['addr'].split('/')[0] for a in nic['addrs']))
            return res
        except StopIteration:
            return None

    def find_disks(self, disk_type):
        """
        return a list of disk that are not used by storage pool
        or has a different type as the one required for this cluster
        """
        available_disks = {}
        for disk in self.disks.list():
            # skip disks of wrong type
            if disk.type.name != disk_type:
                continue
            # skip devices which have filesystems on the device
            if len(disk.filesystems) > 0:
                continue

            # include devices which have partitions
            if len(disk.partitions) == 0:
                available_disks.setdefault(self.name, []).append(disk)

        return available_disks

    def freeports(self, baseport=2000, nrports=3):
        ports = self.client.info.port()
        usedports = set()
        for portInfo in ports:
            if portInfo['network'] != "tcp":
                continue
            usedports.add(portInfo['port'])

        freeports = []
        while True:
            if baseport not in usedports:
                freeports.append(baseport)
                if len(freeports) >= nrports:
                    return freeports
            baseport += 1

    def partition_and_mount_disks(self):
        mounts = []
        node_mountpoints = self.client.disk.mounts()

        for disk in self.disks.list():
            # this check is there to be able to test with a qemu setup. Not needed if you start qemu with --nodefaults
            if disk.model in ['QEMU HARDDISK   ', 'QEMU DVD-ROM    ']:
                continue

            # temporary fix to ommit overwriting the usb boot disk
            if disk.transport == 'usb':
                continue

            if not disk.partitions:
                sp = self.storagepools.create(disk.name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
                devicename = sp.devices[0]
            else:
                if len(disk.partitions) > 1:
                    raise RuntimeError('Found more than 1 partition for disk %s' % disk.name)

                partition = disk.partitions[0]
                devicename = partition.devicename
                sps = self.storagepools.list(devicename)
                if len(sps) > 1:
                    raise RuntimeError('Found more than 1 storagepool for device %s' % devicename)
                elif not sps:
                    sp = self.storagepools.create(disk.name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
                else:
                    sp = sps[0]

            sp.mount()
            if sp.exists(disk.name):
                fs = sp.get(disk.name)
            else:
                fs = sp.create(disk.name)

            mount_point = '/mnt/zdbs/{}'.format(disk.name)
            self.client.filesystem.mkdir(mount_point)

            device_mountpoints = node_mountpoints.get(devicename, [])
            for device_mountpoint in device_mountpoints:
                if device_mountpoint['mountpoint'] == mount_point:
                    break
            else:
                subvol = 'subvol={}'.format(fs.subvolume)
                self.client.disk.mount(sp.devicename, mount_point, [subvol])

            mounts.append({'disk': disk.name, 'mountpoint': mount_point})

        return mounts

    def download_content(self, remote):
        buff = BytesIO()
        self.client.filesystem.download(remote, buff)
        return buff.getvalue().decode()

    def upload_content(self, remote, content):
        if isinstance(content, str):
            content = content.encode('utf8')
        bytes = BytesIO(content)
        self.client.filesystem.upload(remote, bytes)

    def wipedisks(self):
        logger.debug('Wiping node {hostname}'.format(**self.client.info.os()))

        jobs = []
        # for disk in self.client.disk.list():
        for disk in self.disks.list():
            if disk.type == StorageType.CDROM:
                logger.debug('   * Not wiping cdrom {kname} {model}'.format(**disk._disk_info))
                continue

            if disk.transport == 'usb':
                logger.debug('   * Not wiping usb {kname} {model}'.format(**disk._disk_info))
                continue

            if not disk.mountpoint:
                logger.debug('   * Wiping disk {kname}'.format(**disk._disk_info))
                jobs.append(self.client.system('dd if=/dev/zero of={} bs=1M count=50'.format(disk.devicename)))
            else:
                logger.debug('   * Not wiping {device} mounted at {mountpoint}'.format(device=disk.devicename, mountpoint=disk.mountpoint))

        # wait for wiping to complete
        for job in jobs:
            job.get()

    def list_mounts(self):
        allmounts = []
        for mount in self.client.info.disk():
            allmounts.append(Mount(mount['device'],
                                   mount['mountpoint'],
                                   mount['fstype'],
                                   mount['opts']))
        return allmounts

    def is_running(self, timeout=30):
        state = False
        start = time.time()
        err = None
        while time.time() < start + timeout:
            try:
                self.client.testConnectionAttempts = 0
                state = self.client.ping()
                break
            except (RuntimeError, ConnectionError, redis.ConnectionError, redis.TimeoutError, TimeoutError) as error:
                err = error
                time.sleep(1)
        else:
            logger.debug("Could not ping %s within 30 seconds due to %s" % (self.addr, err))

        return state

    def uptime(self):
        response = self.client.system('cat /proc/uptime').get()
        output = response.stdout.split(' ')
        return float(output[0])

    def __str__(self):
        return "Node <{host}:{port}>".format(
            host=self.addr,
            port=self.port,
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        a = "{}:{}".format(self.addr, self.port)
        b = "{}:{}".format(other.addr, other.port)
        return a == b

    def __hash__(self):
        return hash((self.addr, self.port))
