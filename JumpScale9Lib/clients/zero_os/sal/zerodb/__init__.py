from .zerodb import Zerodb
from ..abstracts import DynamicCollection


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
                zdb = Zerodb(self.node, container.name.replace('zdb_', ''))
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
            # this check is there to be able to test with a qemu setup. Not needed if you start qemu with --nodefaults
            if disk.model in ['QEMU HARDDISK   ', 'QEMU DVD-ROM    ']:
                continue

            # temporary fix to ommit overwriting the usb boot disk
            if disk.transport == 'usb':
                continue

            if not disk.partitions:
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
                    sp = self.node.storagepools.create(disk.name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
                else:
                    sp = sps[0]

            if not sp.mountpoint:
                sp.mount()
            if sp.exists(disk.name):
                fs = sp.get(disk.name)
            else:
                fs = sp.create(disk.name)

            mount_point = '/mnt/zdbs/{}'.format(disk.name)
            self.node.client.filesystem.mkdir(mount_point)

            device_mountpoints = node_mountpoints.get(devicename, [])
            for device_mountpoint in device_mountpoints:
                if device_mountpoint['mountpoint'] == mount_point:
                    break
            else:
                subvol = 'subvol={}'.format(fs.subvolume)
                self.node.client.disk.mount(sp.devicename, mount_point, [subvol])

            mounts.append({'disk': disk.name, 'mountpoint': mount_point})

        return mounts


    def create_and_mount_subvolume(self, storagepool, name, size):
        fs = storagepool.create(name, size * (1024 ** 3))
        mount_point = '/mnt/zdbs/{}'.format(name)
        self._node_sal.client.filesystem.mkdir(mount_point)
        subvol = 'subvol={}'.format(fs.subvolume)
        self._node_sal.client.disk.mount(sp.devicename, mount_point, [subvol])

        return mount_point, fs.name