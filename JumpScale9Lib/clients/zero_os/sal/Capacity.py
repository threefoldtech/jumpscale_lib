import io
from js9 import j


class Capacity:

    def __init__(self, node):
        self._node = node
        self._hw_info = None
        self._disk_info = None

    @property
    def hw_info(self):
        if self._hw_info is None:
            out = io.StringIO()

            def cb(level, msg, flag):
                out.write(msg)
                out.write('\n')
            self._node.client.system('dmidecode', stream=True).stream(cb)
            self._hw_info = j.tools.capacity.parser.hw_info_from_dmi(out.getvalue())
        return self._hw_info

    @property
    def disk_info(self):
        if self._disk_info is None:
            self._disk_info = {}
            for disk in self._node.disks.list():
                out = io.StringIO()

                def cb(level, msg, flag):
                    out.write(msg)
                    out.write('\n')
                self._node.client.system('smartctl -i %s' % disk.devicename, stream=True).stream(cb)
                self._disk_info[disk.devicename] = j.tools.capacity.parser.disk_info_from_smartctl(
                    out.getvalue(),
                    disk.size,
                    disk.type.name,
                )
        return self._disk_info

    def report(self, indent=None):
        """
        create a report of the total hardware capacity for
        processor, memory, motherboard and disks
        """
        return j.tools.capacity.parser.get_report(self._node.client.info.mem()['total'], self.hw_info, self.disk_info, indent=indent)

    def actual_use_report(self, total_report):
        """
        create a report of the actual used hardware capacity for
        processor, memory, motherboard and disks
        """
        res = {}
        gib = 1024 * 1024 * 1024

        # Get actual used memory
        memory_available_report = self._node.client.aggregator.query("machine.memory.ram.available").get(
            "machine.memory.ram.available"
        )
        if memory_available_report:
            memory_available = memory_available_report['current']['3600']['avg']
        else:
            memory_available = 0
        res['MRU'] = total_report.MRU - round((memory_available / gib), 2)

        # Get actual used disks
        disks_free_space = self._node.client.aggregator.query("disk.size.free")
        res["HRU"] = total_report.HRU
        res["SRU"] = total_report.SRU
        for disk in total_report.disk:
            disk_name = disk['name'].replace('/dev/', '')
            free_spaces = [value['current']['3600']['avg'] for key, value in disks_free_space.items()
                           if disk_name in key.lower()]
            free_space = sum(free_spaces) / gib
            if disk['type'] in ["HDD", "ARCHIVE"]:
                res['HRU'] -= free_space
            elif disk['type'] in ["SSD", "NVME"]:
                res['SRU'] -= free_space
        res['HRU'] = round(res['HRU'], 2)
        res['SRU'] = round(res['SRU'], 2)

        # Get actual used cpu
        cpu_percentages = [value['current']['3600']['avg']
                           for value in self._node.client.aggregator.query("machine.CPU.percent").values()]
        res['CRU'] = round(sum(cpu_percentages) * sum(cpu_percentages) / 100, 2)
        return res

    def get(self, farmer_id):
        """
        get the capacity object of the node

        :return: Capacity object
        :rtype: dict
        """
        report = self.report()
        used_report = self.actual_use_report(report)
        public_addr = self._node.public_addr
        if public_addr:
            robot_address = "http://%s:6600" % self._node.public_addr
        else:
            robot_address = ""
        os_version = "{branch} {revision}".format(**self._node.client.info.version())

        capacity = dict(
            node_id=self._node.name,
            location=report.location,
            total_resources=dict(
                cru=report.CRU,
                mru=report.MRU,
                hru=report.HRU,
                sru=report.SRU
            ),
            used_resources=dict(
                cru=used_report['CRU'],
                mru=used_report['MRU'],
                hru=used_report['HRU'],
                sru=used_report['SRU'],
            ),
            robot_address=robot_address,
            os_version=os_version,
            farmer_id=farmer_id,
            uptime=int(self._node.uptime())
        )
        return capacity

    def register(self):
        farmer_id = self._node.kernel_args.get('farmer_id')
        if not farmer_id:
            return False

        data = self.get(farmer_id)

        if 'private' in self._node.kernel_args:
            data['robot_address'] = 'private'
        elif not data['robot_address']:
            raise RuntimeError('Can not register a node without robot_address')

        client = j.clients.grid_capacity.get(interactive=False)
        client.api.RegisterCapacity(data)
