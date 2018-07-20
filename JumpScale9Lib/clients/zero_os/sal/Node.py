import time
from collections import namedtuple
from datetime import datetime
from io import BytesIO

import netaddr
import redis
import uuid
import threading
from js9 import j

from .Capacity import Capacity
from .Container import Containers
from .Disk import Disks, StorageType
from .healthcheck import HealthCheck
from .Network import Network
from .StoragePool import StoragePools
from .gateway import Gateways
from .zerodb import Zerodbs
from .primitives import Primitives
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
        self.gateways = Gateways(self)
        self.zerodbs = Zerodbs(self)
        self.primitives = Primitives(self)
        self.hypervisor = Hypervisor(self)
        self.network = Network(self)
        self.healthcheck = HealthCheck(self)
        self.capacity = Capacity(self)
        self.client = client

    @property
    def name(self):
        nics = self.client.info.nic()
        macgwdev, _ = self.get_nic_hwaddr_and_ip(nics)
        if not macgwdev:
            raise AttributeError("name not found for node {}".format(self))
        return macgwdev.replace(":", '')

    @property
    def kernel_args(self):
        args = self.download_content('/proc/cmdline').split()
        result = dict()
        for arg in args:
            split = arg.split('=')
            value = split[1] if len(split) > 1 else ''
            result[split[0]] = value
        return result

    def shell(self):
        """
        Pseudo shell interactive ash shell will be triggered
        Full line commands can be send to the shell (not tabcomplete or fancyness though)
        """
        fifofile = "/tmp/{}".format(uuid.uuid4())
        self.client.system('mkfifo {}'.format(fifofile))
        proc = self.client.bash('ash < {}'.format(fifofile), stream=True)
        reader = threading.Thread(target=proc.stream)
        reader.start()

        writer = self.client.filesystem.open(fifofile, 'w')
        while True:
            try:
                cmd = input('# ').encode('utf-8')
            except EOFError:
                break
            if cmd:
                self.client.filesystem.write(writer, cmd + b";pwd\n")
        self.client.filesystem.close(writer)
        self.client.filesystem.remove(fifofile)
        self.client.job.kill(proc.id, 9)

    @property
    def storageAddr(self):
        if not self._storageAddr:
            nic_data = self.client.info.nic()
            for nic in nic_data:
                if nic['name'] == 'backplane':
                    self._storageAddr = self.get_ip_from_nic(nic['addrs'])
                    return self._storageAddr
            self._storageAddr = self.addr
        return self._storageAddr

    @property
    def public_addr(self):
        nics = self.client.info.nic()
        for nic in nics:
            if nic['name'].startswith('zt'):
                return self.get_ip_from_nic(nic['addrs'])
        _, ip = self.get_nic_hwaddr_and_ip(nics)
        return ip

    def generate_zerotier_identity(self):
        return self.client.system('zerotier-idtool generate').get().stdout.strip()

    def get_nic_hwaddr_and_ip(self, nics, name=None):
        if not name:
            name = self.client.bash("ip route | grep default | awk '{print $5}'", max_time=60).get().stdout.strip()
        for nic in nics:
            if nic['name'] == name:
                return nic['hardwareaddr'], self.get_ip_from_nic(nic['addrs'])
        return '', ''

    def get_ip_from_nic(self, addrs):
        for ip in addrs:
            network = netaddr.IPNetwork(ip['addr'])
            if network.version == 4:
                return network.ip.format()

    def get_nic_by_ip(self, addr):
        try:
            res = next(nic for nic in self.client.info.nic() if any(addr == a['addr'].split('/')[0] for a in nic['addrs']))
            return res
        except StopIteration:
            return None

    def _eligible_zeroos_cache_disk(self, disks):
        """
        return the first disk that is eligible to be used as filesystem cache
        First try to find a ssd disk, otherwise return a HDD
        """
        priorities = [StorageType.SSD, StorageType.HDD, StorageType.NVME]
        eligible = {t: [] for t in priorities}
        # Pick up the first ssd
        usedisks = []
        for pool in (self.client.btrfs.list() or []):
            for device in pool['devices']:
                usedisks.append(device['path'])
        for disk in disks[::-1]:
            if disk.devicename in usedisks or len(disk.partitions) > 0:
                continue
            if disk.type in priorities:
                eligible[disk.type].append(disk)
        # pick up the first disk according to priorities
        for t in priorities:
            if eligible[t]:
                return eligible[t][0]
        else:
            raise RuntimeError("cannot find eligible disks for the fs cache")

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

    def _mount_zeroos_cache(self, storagepool):
        """
        mount the zeroos_cache storage pool and copy the content of the in memmory fs inside
        """
        mountedpaths = [mount.mountpoint for mount in self.list_mounts()]

        def create_cache_dir(path, name):
            self.client.filesystem.mkdir(path)
            if path not in mountedpaths:
                if storagepool.exists(name):
                    storagepool.get(name).delete()
                fs = storagepool.create(name)
                self.client.disk.mount(storagepool.devicename, path, ['subvol={}'.format(fs.subvolume)])

        create_cache_dir('/var/cache/containers', 'containercache')
        create_cache_dir('/var/cache/vm', 'vmcache')

        logpath = '/var/log'
        if logpath not in mountedpaths:
            # logs is empty filesystem which we create a snapshot on to store logs of current boot
            snapname = '{:%Y-%m-%d-%H-%M}'.format(datetime.now())
            fs = storagepool.get('logs')
            snapshot = fs.create(snapname)
            self.client.bash('mkdir /tmp/log && mv /var/log/* /tmp/log/')
            self.client.disk.mount(storagepool.devicename, logpath, ['subvol={}'.format(snapshot.subvolume)])
            self.client.bash('mv /tmp/log/* /var/log/').get()
            self.client.log_manager.reopen()
            # startup syslogd and klogd
            self.client.system('syslogd -n -O /var/log/messages')
            self.client.system('klogd -n')

    def freeports(self, baseport=2000, nrports=3):
        """
        Find free ports on node starting at baseport

        Checks all portfowards + listening ports on host
        to find a free port

        :param baseport: Port to start looking at
        :type baseport: int
        :param nrports: Amount of free ports to find
        :type nrports: int
        :return: list if ports that are free
        :rtype: list(int)
        """
        ports = self.client.info.port()
        usedports = set()
        for portInfo in ports:
            if portInfo['network'] != "tcp":
                continue
            usedports.add(portInfo['port'])
        # Add ports consumed by default forwards
        # TODO: fix this by using core0 api (does not exist yet)
        for container in self.containers.list():
            for port in container.ports:
                port = port.split(':')[-1]  # parse 'zt0:6000' like ports
                usedports.add(int(port))

        freeports = []
        while True:
            if baseport not in usedports:
                freeports.append(baseport)
                if len(freeports) >= nrports:
                    return freeports
            baseport += 1

    def find_persistance(self, name='zos-cache'):
        zeroos_cache_sp = None
        for sp in self.storagepools.list():
            if sp.name == name:
                zeroos_cache_sp = sp
                break
        return zeroos_cache_sp

    def is_configured(self, name='zos-cache'):
        zeroos_cache_sp = self.find_persistance(name)
        if zeroos_cache_sp is None:
            return False
        return bool(zeroos_cache_sp.mountpoint)


    def ensure_persistance(self, name='zos-cache'):
        """
        look for a disk not used,
        create a partition and mount it to be used as cache for the g8ufs
        set the label `zos-cache` to the partition
        """
        disks = self.disks.list()
        if len(disks) <= 0:
            # if no disks, we can't do anything
            return

        # check if there is already a storage pool with the fs_cache label
        zeroos_cache_sp = self.find_persistance(name)

        # create the storage pool if we don't have one yet
        if zeroos_cache_sp is None:
            disk = self._eligible_zeroos_cache_disk(disks)
            zeroos_cache_sp = self.storagepools.create(name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
        zeroos_cache_sp.mount()
        try:
            zeroos_cache_sp.get('logs')
        except ValueError:
            zeroos_cache_sp.create('logs')

        # mount the storage pool
        self._mount_zeroos_cache(zeroos_cache_sp)
        return zeroos_cache_sp

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
                for part in disk.partitions:
                    if part.mountpoint:
                        logger.debug('   * Not wiping {device} because {part} is mounted at {mountpoint}'\
                            .format(device=disk.devicename, part=part.devicename,  mountpoint=part.mountpoint))
                        break
                else:
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

    def get_mount_path(self, path):
        """
        Get the parent mountpoint for a path

        :param path: path you want to retreive the mountpoitn for
        :type path: str
        :rtype: str
        :return: path to the mountpoint
        """
        bestmatch = "/"
        for mount in self.list_mounts():
            if mount.mountpoint in path and len(mount.mountpoint) > len(bestmatch):
                bestmatch = mount.mountpoint
        return bestmatch

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

    def reboot(self):
        self.client.raw('core.reboot', {})

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
