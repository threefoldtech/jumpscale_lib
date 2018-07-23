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

    def total_report(self, indent=None):
        """
        create a report of the total hardware capacity for
        processor, memory, motherboard and disks
        """
        return j.tools.capacity.parser.get_report(self._node.client.info.mem()['total'], self.hw_info, self.disk_info, indent=indent)

    def reality_report(self):
        """
        create a report of the actual used hardware capacity for
        processor, memory, motherboard and disks
        """
        total_report = self.total_report()

        return j.tools.capacity.reality_parser.get_report(
            disks=self._node.disks.list(),
            storage_pools=self._node.storagepools.list(),
            total_cpu_nr=total_report.CRU,
            used_cpu=self._node.client.aggregator.query("machine.CPU.percent"),
            used_memory=self._node.client.info.mem()['used']
        )

    def register(self):
        farmer_id = self._node.kernel_args.get('farmer_id')
        if not farmer_id:
            return False

        robot_address = ""
        public_addr = self._node.public_addr
        if public_addr:
            robot_address = "http://%s:6600" % public_addr
        os_version = "{branch} {revision}".format(**self._node.client.info.version())

        report = self.total_report()
        data = dict(
            node_id=self._node.name,
            location=report.location,
            total_resources=dict(
                cru=report.CRU,
                mru=report.MRU,
                hru=report.HRU,
                sru=report.SRU
            ),
            robot_address=robot_address,
            os_version=os_version,
            uptime=int(self._node.uptime())
        )
        data['farmer_id'] = farmer_id

        if 'private' in self._node.kernel_args:
            data['robot_address'] = 'private'
        elif not data['robot_address']:
            raise RuntimeError('Can not register a node without robot_address')

        client = j.clients.grid_capacity.get(interactive=False)
        _, resp = client.api.RegisterCapacity(data)
        resp.raise_for_status()

    def update_reality(self):
        farmer_id = self._node.kernel_args.get('farmer_id')
        if not farmer_id:
            return False

        report = self.reality_report()
        data = dict(
            node_id=self._node.name,
            farmer_id=farmer_id,
            cru=report.CRU,
            mru=report.MRU,
            hru=report.HRU,
            sru=report.SRU,
        )

        client = j.clients.grid_capacity.get(interactive=False)
        resp = client.api.UpdateActualUsedCapacity(data=data, node_id=self._node.name)
        resp.raise_for_status()

    def update_reserved(self, vms, vdisks, gateways):
        farmer_id = self._node.kernel_args.get('farmer_id')
        if not farmer_id:
            return False

        report = j.tools.capacity.reservation_parser.get_report(vms, vdisks, gateways)
        data = dict(
            node_id=self._node.name,
            farmer_id=farmer_id,
            cru=report.CRU,
            mru=report.MRU,
            hru=report.HRU,
            sru=report.SRU,
        )

        client = j.clients.grid_capacity.get(interactive=False)
        resp = client.api.UpdateReservedCapacity(data=data, node_id=self._node.name)
        resp.raise_for_status()
