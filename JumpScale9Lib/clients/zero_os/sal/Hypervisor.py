from js9 import j

logger = j.logger.get(__name__)


class Hypervisor:

    def __init__(self, name, uuid, node):
        self.name = name
        self.uuid = uuid
        self.node = node

    def create(self, media=None, flist=None, cpu=2, memory=512, nics=None, port=None, mount=None, tags=None):
        logger.info('Creating kvm %s' % self.name)
        return self.node.client.kvm.create(name=self.name,
                                           media=media,
                                           flist=flist,
                                           cpu=cpu,
                                           memory=memory,
                                           nics=nics,
                                           port=port,
                                           mount=mount,
                                           tags=tags)

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
