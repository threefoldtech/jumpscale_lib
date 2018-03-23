from js9 import j

logger = j.logger.get(__name__)

class VM:
    def __init__(self, uuid, node, info=None):
        self.node = node
        self.uuid = uuid
        self._info = info

    def destroy(self):
        logger.info('Destroying kvm with uuid %s' % self.uuid)
        self.node.client.kvm.destroy(self.uuid)

    def shutdown(self):
        logger.info('Shuting down kvm with uuid %s' % self.uuid)
        self.node.client.kvm.shutdown(self.uuid)

    def pause(self):
        logger.info('Pausing kvm with uuid %s' % self.uuid)
        self.node.client.kvm.pause(self.uuid)

    def reboot(self):
        logger.info('Rebooting kvm with uuid %s' % self.uuid)
        self.node.client.kvm.reboot(self.uuid)

    def reset(self):
        logger.info('Reseting kvm with uuid %s' % self.uuid)
        self.node.client.kvm.reset(self.uuid)

    def resume(self):
        logger.info('Resuming kvm with uuid %s' % self.uuid)
        self.node.client.kvm.resume(self.uuid)

    @property
    def info(self):
        if self._info is None:
            for vminfo in self.node.client.kvm.list():
                if vminfo['uuid'] == self.uuid:
                    self._info = vminfo
        return self._info

    def enable_vnc(self):
        port = self.info['vnc']
        if port:
            logger.info('Enabling vnc for port %s' % port)
            self.node.client.nft.open_port(port)

    def disable_vnc(self):
        port = self.info['vnc']
        if port:
            logger.info('Disabling vnc for port %s' % port)
            self.node.client.nft.drop_port(port)

    def __str__(self):
        return "VM <{}>".format(self.info['name'])

    def __repr__(self):
        return str(self)

