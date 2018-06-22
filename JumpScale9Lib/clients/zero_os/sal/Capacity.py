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
        create a report of the hardware capacity for
        processor, memory, motherboard and disks
        """
        return j.tools.capacity.parser.get_report(self._node.client.info.mem()['total'], self.hw_info, self.disk_info, indent=indent)

    def get(self, farmer_id):
        """
        get the capacity object of the node

        :return: Capacity object
        :rtype: dict
        """
        report = self.report()
        robot_address = "http://%s:6600" % self._node.public_addr
        os_version = "{branch} {revision}".format(**self._node.client.info.version())

        capacity = dict(
            node_id=self._node.name,
            location=report.location,
            cru=report.CRU,
            mru=report.MRU,
            hru=report.HRU,
            sru=report.SRU,
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

        client = j.clients.grid_capacity.get(interactive=False)
        client.api.RegisterCapacity(data)
        return True
