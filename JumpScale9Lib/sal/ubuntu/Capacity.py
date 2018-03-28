import json
import psutil

from js9 import j
from JumpScale9Lib.tools.capacityparser.CapacityParser import StorageType

class Capacity:

    def __init__(self, node):
        self._node = node
        self._hw_info = None
        self._disk_info = None

    @property
    def hw_info(self):
        if self._hw_info is None:
            self._node.apt_install_check("dmidecode", "dmidecode")

            rc, dmi_data, err = self._node._local.execute("dmidecode", die=False)
            if rc != 0:
                raise RuntimeError("Error getting hardware info:\n%s" % (err))
                
            self._hw_info = j.tools.capacityparser.hw_info_from_dmi(dmi_data)
        return self._hw_info

    @property
    def disk_info(self):
        if self._disk_info is None:
            self._node.apt_install_check("smartmontools", "smartctl")
            self._disk_info = {}

            rc, out, err = self._node._local.execute(
                "lsblk -J -o NAME,SIZE,ROTA,TYPE", die=False)
            if rc != 0:
                raise RuntimeError("Error getting disks:\n%s" % (err))

            disks = json.loads(out)["blockdevices"]
            for disk in disks:
                rc, out, err = self._node._local.execute(
                    "smartctl -T permissive -i /dev/%s" % disk["name"], die=False)
                if rc != 0:
                    # smartctl prints error on stdout
                    raise RuntimeError("Error getting disk data for %s:\n%s\n\n%s" % (disk["name"], out, err))

                self._disk_info[disk["name"]] = j.tools.capacityparser.disk_info_from_smartctl(
                    out,
                    disk["size"],
                    _disk_type(disk).name,
                )
        return self._disk_info

    def report(self):
        """
        create a report of the hardware capacity for
        processor, memory, motherboard and disks
        """
        return j.tools.capacityparser.get_report(psutil.virtual_memory().total, self.hw_info, self.disk_info)


def _disk_type(disk_info):
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
            return StorageType.HDD
    else:
        if "nvme" in disk_info['name']:
            return StorageType.NVME
        else:
            return StorageType.SSD
