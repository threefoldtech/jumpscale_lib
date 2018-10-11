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
            if container.name.startswith('zerodb_'):
                zdb = Zerodb(self.node, container.name.lstrip('zerodb_'))
                zdb.load_from_reality(container)
                zdbs.append(zdb)
        return zdbs

    def create(self, name, path=None, mode='user', sync=False, admin=''):
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
        return Zerodb(self.node, name, path, mode, sync, admin)

    def partition_and_mount_disks(self):
        mounts = []

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

            name = j.data.idgenerator.generateGUID()
            if not disk.partitions:
                logger.info("create storage pool on %s" % disk.devicename)
                sp = self.node.storagepools.create(name, device=disk.devicename, metadata_profile='single', data_profile='single', overwrite=True)
            else:
                if len(disk.partitions) > 1:
                    raise RuntimeError('Found more than 1 partition for disk %s' % disk.name)

                partition = disk.partitions[0]
                sps = self.node.storagepools.list(partition.fs_uuid)
                if len(sps) > 1:
                    raise RuntimeError('Found more than 1 storagepool for fs_uuid %s' % partition.fs_uuid)
                elif not sps:
                    logger.info("create storage pool on %s" % disk.devicename)
                    sp = self.node.storagepools.create(name, device=disk.devicename, metadata_profile='single', data_profile='single', overwrite=True)
                else:
                    sp = sps[0]

            if not sp.mountpoint:
                sp.mount()
            if not sp.exists(sp.name):
                logger.info("create filesystem on %s" % disk.devicename)
                sp.create(sp.name)

            mounts.append({'disk': disk.name, 'mountpoint': sp.mountpoint})

        return mounts

    def create_and_mount_subvolume(self, zdb_name, size, disktypes):
        # filter storagepools that have the correct disk type and whose (total size - reserved subvolume quota) >= size
        storagepools = list(filter(lambda sp: self.node.disks.get_device(sp.device).disk.type.value in disktypes and (sp.size - sp.total_quota() / (1024 ** 3)) >= size,
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

        old_zdb = zdb_name.split('_')[-1]  # this is for backward compatability
        for storagepool in self.node.storagepools.list():
            for fs in storagepool.list():
                if fs.name == 'zdb_{}'.format(zdb_name) or fs.name == 'zdb_{}'.format(old_zdb):
                    self.node.client.filesystem.mkdir(mount_point)
                    subvol = 'subvol={}'.format(fs.subvolume)
                    self.node.client.disk.mount(storagepool.devicename, mount_point, [subvol])
                    break
        else:
            raise RuntimeError('Failed to find filesystem for zerodb {}'.format(zdb_name))
