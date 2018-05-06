from js9 import j
from .VM import VM

logger = j.logger.get(__name__)


class Hypervisor:
    def __init__(self, node):
        self.node = node

    def create(self, name, flist=None, vcpus=2, memory=2048):
        logger.info('Creating kvm %s' % name)
        return VM(self.node, name, flist, vcpus, memory)

    def list(self):
        for vm in self.node.client.kvm.list():
            vm = VM(self.node, vm['name'])
            vm.load_from_reality()
            yield vm

    def get(self, name):
        vm = VM(self.node, name)
        vm.load_from_reality()
        return vm

