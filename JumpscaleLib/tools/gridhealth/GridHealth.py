from Jumpscale import j
from urllib.parse import urlparse
import redis
import time

JSBASE = j.application.JSBaseClass

class GridHealth(JSBASE):
    """
    Monitor and Manage ThreeFold Grid and Nodes
    """

    def __init__(self, node=None, robot=None):
        """
        Connect to a remote Zero-OS server, based on multiple possibilities:
         - node: from a Node object (j.clients.zos.get)
         - robot: from a Robot object (j.clients.zrobot.get)
        """
        self.log = j.logger.get("gridhealth")

        if not node and not robot:
            raise RuntimeError("Please provide at least one Node or one Robot")

        if node:
            self._node = node
            self._robot = self._getrobot()

        if robot:
            self._robot = robot
            self._node = self._getnode()

        try:
            self._node.ping()

        except redis.ResponseError:
            self.log.warning("Cannot reach the node, partial report available")
            self._node = NodeStub()

        self._supportzt = '1d71939404587f3c'
        self._farmerzt = 'c7c8172af1f387a6'

    #
    # Initializers
    #
    def _getrobot(self):
        """ Get a robot from node object """

        raddr = 'http://%s:6600' % self.node.addr
        return j.clients.zrobot.get(instance=self.node.addr, data={'url': raddr})

    def _getnode(self):
        """ Get a node from robot object """

        naddr = urlparse(self._robot.config.data['url'])
        return j.clients.zos.get(instance=naddr.hostname, data={'host': naddr.hostname})

    #
    # Basic Operations
    #
    @property
    def node(self):
        return self._node

    def version(self):
        return self.node.client.info.version()

    def system(self):
        return self.node.client.info.os()

    def parameters(self):
        return self.node.kernel_args

    def git_info(self, container, path):
        branch = container.bash("cd /%s && (git symbolic-ref -q --short HEAD || git describe --tags --exact-match)" % path).get()
        commit = container.bash("cd /%s && git log --format='%%H' -n 1" % path).get()

        return {'branch': branch.stdout.strip(), 'commit': commit.stdout.strip()}

    #
    # Robot
    #
    def robot_info(self):
        info = self.node.client.container.find("zrobot")

        if len(info) != 1:
            return None

        return info

    def robot_version(self):
        info = self.robot_info()
        repositories = ['0-robot', 'jumpscale_core', 'jumpscale_lib']
        response = {}

        if info == None:
            for repository in repositories:
                response[repository] = {'branch': 'unavailable', 'commit': 'unavailable'}

            return response

        client = self.node.client.container.client(list(info.keys())[0])

        for repository in repositories:
            fullpath = '/opt/code/github/threefoldtech/%s' % repository
            response[repository] = self.git_info(client, fullpath)

        return response

    def robot_health(self):
        info = self._robot.api.robot.GetRobotInfo()[0].as_dict()
        services = self._robot.api.services.listServices()[1]

        healthy = (services.status_code == 200)

        return {'storage_healthy': info['storage_healthy'], 'healthy': healthy}

    def zerotier_status(self, netid):
        ztnet = self.node.client.zerotier.list()

        for zt in ztnet:
            if zt['nwid'] != netid:
                continue

            if zt['status'] != 'OK':
                return {'status': zt['status']}

            if len(zt['assignedAddresses']) < 1:
                return {'status': 'no address assigned'}

            ztaddr = zt['assignedAddresses'][0].partition('/')[0]

            return {'status': 'OK', 'address': ztaddr}

        return {'status': 'not attached'}

    #
    # Support Mode
    #
    def support_zt(self):
        return self.zerotier_status(self._supportzt)

    #
    # Farmer Network
    #
    def farmer_zt(self):
        return self.zerotier_status(self._farmerzt)

    #
    # General Report
    #
    def report(self):
        parameters = self.parameters()

        response = {
            'name': self.node.name,
            'version': self.version(),
            'system': self.system(),
            'parameters': parameters,
            'modes': {
                'development': "development" in parameters,
                'support': "support" in parameters,
                'debug': "debug" in parameters
            },
            'robot': {
                'version': self.robot_version(),
                'health': self.robot_health(),
            },
            'support': self.support_zt(),
            'farmer': self.farmer_zt(),
        }

        return response


class GridHealthQuery(JSBASE):
    def __init__(self):
        self.log = j.logger.get("gridquery")

        self.timelimit = 7 * 86400   # 7 days
        self.supportnet = "172.29"

    #
    # Capacity Listing
    #
    def nodes(self, farmerid=None, offline=False):
        self.log.info("fetching nodes list")
        nodes = j.clients.threefold_directory.capacity

        # nothing to do if we want full list
        # let's just forward it as it
        if farmerid == None and offline == True:
            return nodes

        knodes = []
        timenow = time.time()

        for node in nodes:
            if not offline:
                # reject nodes without updated flags
                if not node['updated']:
                    continue

                # do not includes offline nodes
                if node['updated'] < timenow - self.timelimit:
                    continue

            # append if no farmer id was set, or if farmerid matches
            if farmerid == None or node['farmer_id'] == farmerid:
                knodes.append(node)

        return knodes

    def node_address(self, node):
        raddr = node['robot_address']
        return raddr.partition('//')[2].partition(':')[0]

    def nodes_addresses(self, nodes):
        addresses = []

        for node in nodes:
            addresses.append(self.node_address(node))

        return addresses

    def node_support_translate(self, address):
        sg = address.split(".")
        return "%s.%s.%s" % (self.supportnet, sg[2], sg[3])

    def nodelist_report_support(self, nodes):
        reports = {}

        for node in nodes:
            addr = self.node_address(node)
            reports[addr] = {
                'target': self.node_support_translate(addr),
                'report': {}
            }

        # gevent ?
        for source in reports.keys():
            target = reports[source]['target']

            self.log.info("fetching node: %s (%s)" % (source, target))
            node = j.clients.zos.get(target, data={'host': target})

            c = GridHealth(node)
            reports[source]['report'] = c.report()

        return reports

    def farmers(self):
        return j.clients.threefold_directory.farmers


class NodeStub:
    def __init__(self):
        self.name = 'unavailable'
        self.client = self.Client()
        self.kernel_args = {}

    class Client:
        def __init__(self):
            self.info = self.Info()
            self.container = self.Container()
            self.zerotier = self.Zerotier()

        class Info:
            def version(self):
                return {'branch': 'unavailable', 'revision': 'unavailable'}

            def os(self):
                return {'os': 'unavailable', 'hostname': 'unavailable', 'uptime': 0}

        class Container:
            def find(self, keyword):
                return {}

        class Zerotier:
            def list(self):
                return {}
