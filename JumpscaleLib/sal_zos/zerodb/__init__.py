from .zerodb import Zerodb
from ..abstracts import DynamicCollection
from ..disks.Disks import StorageType

from jumpscale import j

logger = j.logger.get(__name__)


class Zerodbs(DynamicCollection):
    def __init__(self, node):
        self.node = node

    def get(self, name):
        """
        Get zerodb object and load data from reality

        :param name: Name of the zerodb
        :type name: str

        :return: Zerodb object
        :rtype: Zerodb object
        """
        zdb = Zerodb(self.node, name)
        zdb.load_from_reality()
        return zdb

    def list(self):
        """
        list zerodb objects

        :return: list of Zerodb object
        :rtype: list
        """
        zdbs = []
        for container in self.node.containers.list():
            if container.name.startswith('zdb_'):
                zdb = Zerodb(self.node, container.name)
                zdb.load_from_reality(container)
                zdbs.append(zdb)
        return zdbs

    def create(self, name, path=None, mode='user', sync=False, admin='', node_port=9900):
        """
        Create zerodb object

        To deploy zerodb invoke .deploy method

        :param name: Name of the zerodb
        :type name: str
        :param path: path zerodb stores data on
        :type path: str
        :param mode: zerodb running mode
        :type mode: str
        :param sync: zerodb sync
        :type sync: bool
        :param admin: zerodb admin password
        :type admin: str

        :return: Zerodb object
        :rtype: Zerodb object
        """
        return Zerodb(self.node, name, path, mode, sync, admin, node_port)

    def partition_and_mount_disks(self):
        mounts = []
        node_mountpoints = self.node.client.disk.mounts()

        for disk in self.node.disks.list():
            if disk.type not in [StorageType.HDD, StorageType.SSD, StorageType.NVME, StorageType.ARCHIVE]:
                logger.info("skipping unsupported disk type %s" % disk.type)
                continue

            # this check is there to be able to test with a qemu setup. Not needed if you start qemu with --nodefaults
            if disk.model in ['QEMU HARDDISK   ', 'QEMU DVD-ROM    ']:
                continue

            # temporary fix to ommit overwriting the usb boot disk
            if disk.transport == 'usb':
                continue

            logger.info("processing disk %s" % disk.devicename)

            if not disk.partitions:
                logger.info("create storage pool on %s" % disk.devicename)
                sp = self.node.storagepools.create(disk.name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
                devicename = sp.devices[0]
            else:
                if len(disk.partitions) > 1:
                    raise RuntimeError('Found more than 1 partition for disk %s' % disk.name)

                partition = disk.partitions[0]
                devicename = partition.devicename
                sps = self.node.storagepools.list(devicename)
                if len(sps) > 1:
                    raise RuntimeError('Found more than 1 storagepool for device %s' % devicename)
                elif not sps:
                    logger.info("create storage pool on %s" % disk.devicename)
                    sp = self.node.storagepools.create(disk.name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
                else:
                    sp = sps[0]

            if not sp.mountpoint:
                sp.mount()
            if sp.exists(disk.name):
                fs = sp.get(disk.name)
            else:
                logger.info("create filesystem on %s" % disk.devicename)
                fs = sp.create(disk.name)

            mount_point = '/mnt/zdbs/{}'.format(disk.name)
            self.node.client.filesystem.mkdir(mount_point)

            device_mountpoints = node_mountpoints.get(devicename, [])
            for device_mountpoint in device_mountpoints:
                if device_mountpoint['mountpoint'] == mount_point:
                    break
            else:
                logger.info("mount filesystem on %s" % mount_point)
                subvol = 'subvol={}'.format(fs.subvolume)
                self.node.client.disk.mount(sp.devicename, mount_point, [subvol])

            mounts.append({'disk': disk.name, 'mountpoint': mount_point})

        return mounts

    def create_and_mount_subvolume(self, zdb_name, size, disktypes):
        # filter storagepools that have the correct disk type and whose (total size - reserved subvolume quota) >= size
        storagepools = list(filter(lambda sp: self.node.disks.get_device(sp.devices[0]).disk.type.value in disktypes and (sp.size - sp.total_quota() / (1024 ** 3)) >= size,
                                   self.node.storagepools.list()))
        storagepools.sort(key=lambda sp: sp.size - sp.total_quota(), reverse=True)
        if not storagepools:
            return ''

        storagepool = storagepools[0]
        # QUESTION: why this? *3 it's not, it's **3 which is "to the power"
        # so the size is specified in gigabytes (1024x1024x1024)
        fs = storagepool.create('zdb_{}'.format(zdb_name), size * (1024 ** 3))
        mount_point = '/mnt/zdbs/{}'.format(zdb_name)
        self.node.client.filesystem.mkdir(mount_point)
        subvol = 'subvol={}'.format(fs.subvolume)
        self.node.client.disk.mount(storagepool.devicename, mount_point, [subvol])

        return mount_point

    def mount_subvolume(self, zdb_name, mount_point):
        if self.node.client.filesystem.exists(mount_point):
            node_mountpoints = self.node.client.disk.mounts()
            for device in node_mountpoints:
                for mp in node_mountpoints[device]:
                    if mp['mountpoint'] == mount_point:
                        return

        old_zdb = zdb_name.split('_')[-1] # this is for backward compatability
        for storagepool in self.node.storagepools.list():
            for fs in storagepool.list():
                if fs.name == 'zdb_{}'.format(zdb_name) or fs.name == 'zdb_{}'.format(old_zdb):
                    self.node.client.filesystem.mkdir(mount_point)
                    subvol = 'subvol={}'.format(fs.subvolume)
                    self.node.client.disk.mount(storagepool.devicename, mount_point, [subvol])
                    break
        else:
            raise RuntimeError('Failed to find filesystem for zerodb {}'.format(zdb_name))
