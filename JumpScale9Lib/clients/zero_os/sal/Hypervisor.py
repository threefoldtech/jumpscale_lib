from js9 import j
from .VM import VM

logger = j.logger.get(__name__)


class Hypervisor:
    def __init__(self, node):
        self.node = node

    def create(self, name, media=None, flist=None, cpu=2, memory=512, nics=None, ports=None, mounts=None, tags=None, config=None):
        logger.info('Creating kvm %s' % name)
        portmap = j.clients.zero_os.sal.format_ports(ports)
        uuid = self.node.client.kvm.create(name=name,
                                           media=media,
                                           flist=flist,
                                           cpu=cpu,
                                           memory=memory,
                                           nics=nics,
                                           port=portmap,
                                           mount=mounts,
                                           tags=tags,
                                           config=config)
        for port in portmap:
            self.node.client.nft.open_port(port)

        return VM(uuid, self.node)

    def list(self):
        for vm in self.node.client.kvm.list():
            yield VM(vm['uuid'], self.node, vm)

    def get(self, uuid):
        return VM(uuid, self.node)
