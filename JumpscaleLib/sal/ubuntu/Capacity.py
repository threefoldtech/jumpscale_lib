import json

import psutil

from jumpscale import j
from JumpscaleLib.sal_zos.disks.Disks import StorageType


class FakeZOSDisk:
    def __init__(self, name, size, type):
        self.name = name
        self.type = type
        self.size = size


class Capacity:

    def __init__(self, node):
        self._node = node
        self._hw_info = None
        self._disk_info = None
        self._smartmontools_installed = False

    def cpu_info(self):
        """
        Return a dumb list, amount of item on the list
        is the amount of cpu on the host
        """
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()

        cpus = []

        for line in cpuinfo.split("\n"):
            if line.startswith("processor\t:"):
                cpus.append(line)

        return cpus

    def mem_info(self):
        """
        Simulate a core0 response of info.mem()
        from local machine
        """
        with open("/proc/meminfo", "r") as f:
            memfile = f.read()

        memlist = memfile.split("\n")
        meminfo = {}

        for line in memlist:
            temp = line.split()
            if len(temp) < 1:
                break

            meminfo[temp[0]] = int(temp[1]) * 1024

        return {
            'active': meminfo['MemTotal:'],
            'available': meminfo['MemAvailable:'],
            'buffers': meminfo['Buffers:'],
            'cached': meminfo['Cached:'],
            'dirty': meminfo['Dirty:'],
            'free': meminfo['MemFree:'],
            'inactive': meminfo['Inactive:'],
            'pagetables': meminfo['PageTables:'],
            'shared': meminfo['Shmem:'],
            'slab': meminfo['Slab:'],
            'swapcached': 0,
            'total': meminfo['MemTotal:'],
            'used': 0,
            'usedPercent': 0,
            'wired': 0,
            'writeback': 0,
            'writebacktmp': 0
        }

    def disk_info(self):
        if self._disk_info is None:
            self._disk_info = []

            rc, out, err = self._node._local.execute(
                "lsblk -Jb -o NAME,SIZE,ROTA,TYPE", die=False)
            if rc != 0:
                raise RuntimeError("Error getting disks:\n%s" % (err))

            disks = json.loads(out)["blockdevices"]
            for disk in disks:
                if not disk["name"].startswith("/dev/"):
                    disk["name"] = "/dev/%s" % disk["name"]

                if disk["name"].startswith("/dev/loop"):
                    continue

                diskinfo = FakeZOSDisk(disk['name'], disk['size'], self._disk_type(disk))
                self._disk_info.append(diskinfo)

        return self._disk_info

    def report(self, indent=None):
        """
        create a report of the hardware capacity for
        processor, memory, motherboard and disks
        """
        return j.tools.capacity.parser.get_report(self.cpu_info(), self.mem_info(), self.disk_info())

    def get(self, farmer_id):
        """
        get the capacity object of the node

        this capacity object is used in the capacity registration

        :return: dict object ready for capacity registration
        :rtype: dict
        """
        interface, _ = j.sal.nettools.getDefaultIPConfig()
        mac = j.sal.nettools.getMacAddress(interface)
        node_id = mac[0].replace(':', '')
        if not node_id:
            raise RuntimeError("can't detect node ID")

        report = self.report()
        capacity = dict(
            node_id=node_id,
            location=report.location,
            total_resources=dict(
                cru=report.CRU,
                mru=report.MRU,
                hru=report.HRU,
                sru=report.SRU,
            ),
            robot_address="private",
            os_version="private",
            farmer_id=farmer_id,
            uptime=int(self._node.uptime()),
        )
        return capacity

    def register(self, farmer_id):
        if not farmer_id:
            return False
        data = self.get(farmer_id)
        client = j.clients.threefold_directory.get(interactive=False)
        _, resp = client.api.RegisterCapacity(data)
        resp.raise_for_status()
        return True

    def _seektime(self, device):
        cmdname = "seektime -j %s" % device
        rc, out, err = self._node._local.execute(cmdname, die=False)
        if rc != 0:
            raise RuntimeError("Seektime error for %s (Are you on baremetal, not on a VM ?): %s (%s)" % (device, err))

        data = j.data.serializer.json.loads(out)
        if data['type'] == 'HDD':
            return StorageType.HDD

        return StorageType.SSD

    def _disk_type(self, disk_info):
        """
        return the type of the disk
        """
        if disk_info['rota'] == "1":
            if disk_info['type'] == 'rom':
                return StorageType.CDROM

            # assume that if a disk is more than 7TB it's a SMR disk
            elif int(disk_info['size']) > (1024 * 1024 * 1024 * 1024 * 7):
                return StorageType.ARCHIVE
            else:
                return self._seektime(disk_info['name'])
        else:
            if "nvme" in disk_info['name']:
                return StorageType.NVME
            else:
                return StorageType.SSD
