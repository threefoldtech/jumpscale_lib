from js9 import j

logger = j.logger.get(__name__)


class VM:

    def __init__(self, hypervisor_name, node):
        self.hypervisor_name = hypervisor_name
        self.node = node

    def _get_vnc_port(self):
        # Fix me: client.kvm should provide a way to get
        # the info without listing all vms
        for vm in self.node.client.kvm.list():
            if vm['name'] == self.hypervisor_name:
                return vm['vnc']

    def enable_vnc(self):
        port = self._get_vnc_port()
        if port:
            logger.info('Enabling vnc for port %s' % port)
            self.node.client.nft.open_port(port)

    def disable_vnc(self):
        port = self._get_vnc_port()
        if port:
            logger.info('Disabling vnc for port %s' % port)
            self.node.client.nft.drop_port(port)
