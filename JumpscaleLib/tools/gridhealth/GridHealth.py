from Jumpscale import j

JSBASE = j.application.JSBaseClass

class GridHealth(JSBASE):
    """
    Monitor and Manage ThreeFold Grid and Nodes
    """

    def __init__(self, node):
        self._node = node
        self._supportzt = '1d71939404587f3c'
        self._robot = self._getrobot()

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

        if info == None:
            return None

        client = self.node.client.container.client(list(info.keys())[0])
        response = {}

        for repository in ['0-robot', 'jumpscale_core', 'jumpscale_lib']:
            fullpath = '/opt/code/github/threefoldtech/%s' % repository
            response[repository] = self.git_info(client, fullpath)

        return response

    def robot_health(self):
        info = self._robot.api.robot.GetRobotInfo()[0].as_dict()
        services = self._robot.api.services.listServices()[1]

        healthy = (services.status_code == 200)

        return {'storage_healthy': info['storage_healthy'], 'healthy': healthy}

    def _getrobot(self):
        raddr = 'http://%s:6600' % self.node.addr
        return j.clients.zrobot.get(instance=self.node.addr, data={'url': raddr})

    #
    # Support Mode
    #
    def support_zt(self):
        ztnet = self.node.client.zerotier.list()

        for zt in ztnet:
            if zt['nwid'] != self._supportzt:
                continue

            if zt['status'] != 'OK':
                return {'status': zt['status']}

            if len(zt['assignedAddresses']) < 1:
                return {'status': 'no address assigned'}

            ztaddr = zt['assignedAddresses'][0].partition('/')[0]

            return {'status': 'OK', 'address': ztaddr}

        return {'status': 'not attached'}


    #
    # General Report
    #
    def report(self):
        parameters = self.parameters()

        response = {
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
        }

        return response
