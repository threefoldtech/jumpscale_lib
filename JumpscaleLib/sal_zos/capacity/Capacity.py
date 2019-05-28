import io
import re

import requests

from jumpscale import j

logger = j.logger.get(__name__)

_DISK_DUMP_EXPRESSION = re.compile(r"^([^\s]+)\s+-d\s+([^\s]+)\s+#")
_AGGREGATOR_NAME = "minting-py smartctl aggregator v0.1.0"
_HEADER_EXPRESSION = re.compile(r"([^\[]+)\[([^\[]+)\]")
_INFORMATION_EXPRESSION = re.compile(r"([^:]+):\s+(.+)")


def parse_smartctl_stdout(stdout):
    output = {}
    lines = stdout.splitlines()
    if len(lines) == 0:
        return output

    header = _HEADER_EXPRESSION.search(lines[0])
    if len(lines) == 1:
        return output

    output["tool"] = header.group(1).strip()
    output["environment"] = header.group(2).strip()
    information = {}
    for line in lines[1:]:
        pair = _INFORMATION_EXPRESSION.search(line)
        if not pair:
            continue
        information[pair.group(1).strip()] = pair.group(2).strip()
    output["information"] = information
    return output


class Capacity:

    def __init__(self, node):
        self._node = node

    def hardware_dump(self):
        output = self._node.client.info.dmi()
        if isinstance(output, dict) and "tooling" in output:
            return output
        # hardcode tooling section if it is not yet available in this node
        return {
            "tooling": {
                "aggregator": "dmidecode 3.1",
                "decoder": "0-core Go dmi decoder v0.0.9",
            },
            "sections": output,
        }

    def disks_dump(self):
        # fetch all the disks
        buff = io.StringIO()

        def callback(level, msg, flag):
            buff.write(msg)

        # we stream the result in case there are a lot of disk
        # and we cannot get the full output using job.get()
        job = self._node.client.system("smartctl --scan", stream=True)
        job.stream(callback)

        disks = {}
        for line in buff.getvalue().splitlines():
            match = _DISK_DUMP_EXPRESSION.search(line)
            if not match:
                continue
            disks[match.group(1)] = match.group(2)
        dump = []
        for disk_name, disk_type in disks.items():
            result = self._node.client.system("smartctl -i %s -d %s" % (disk_name, disk_type)).get()
            dump.append(parse_smartctl_stdout(result.stdout))
        if len(dump) == 0:
            return {}
        # aggregate disks, so we only have to print tool/environment info once
        info = {
            "tool": dump[0]["tool"],
            "environment": dump[0]["environment"],
            "aggregator": _AGGREGATOR_NAME,
            "devices": [],
        }
        for disk in dump:
            if disk["tool"] != info["tool"]:
                raise RuntimeError("unexpected tool: {} != {}".format(disk["tool"], info["tool"]))
            if disk["environment"] != info["environment"]:
                raise RuntimeError("unexpected environment: {} != {}".format(disk["environment"], info["environment"]))
            info["devices"].append(disk["information"])
        return info

    def total_report(self):
        """
        create a report of the total hardware capacity for
        processor, memory, motherboard and disks
        """
        cl = self._node.client
        n = self._node

        return j.tools.capacity.parser.get_report(cl.info.cpu(), cl.info.mem(), n.disks.list())

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

    def node_parameters(self):
        params = []
        checking = ['development', 'debug', 'support']

        for check in checking:
            if self._node.kernel_args.get(check) is not None:
                params.append(check)

        return params

    def directory(self):
        if 'staging' in self._node.kernel_args:
            # return a staging directory object
            data = {'base_uri': 'https://staging.capacity.threefoldtoken.com'}
            return j.clients.threefold_directory.get('staging', data=data, interactive=False)

        # return production directory
        return j.clients.threefold_directory.get(interactive=False)

    def register(self, include_hardware_dump=False):
        farmer_id = self._node.kernel_args.get('farmer_id')
        if not farmer_id:
            return False

        # checking kernel parameters enabled
        parameters = self.node_parameters()

        robot_address = ""
        public_addr = self._node.public_addr
        if public_addr:
            robot_address = "http://%s:6600" % public_addr
        os_version = "{branch} {revision}".format(**self._node.client.info.version())

        report = self.total_report()
        data = dict(
            node_id=self._node.name,
            location=report.location,
            total_resources=report.total(),
            robot_address=robot_address,
            os_version=os_version,
            parameters=parameters,
            uptime=int(self._node.uptime())
        )

        if include_hardware_dump:
            data['hardware'] = self.hardware_dump()
            data['disks'] = self.disks_dump()

        data['farmer_id'] = farmer_id

        if 'private' in self._node.kernel_args:
            data['robot_address'] = 'private'
        elif not data['robot_address']:
            raise RuntimeError('Can not register a node without robot_address')

        client = self.directory()

        try:
            _, resp = client.api.RegisterCapacity(data)
        except requests.exceptions.HTTPError as err:
            logger.error("error pusing total capacity to the directory: %s" % err.response.content)

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

        client = self.directory()

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

        client = self.directory()

        resp = client.api.UpdateReservedCapacity(data=data, node_id=self._node.name)
        resp.raise_for_status()
