from jumpscale import j
from framework.base.zdb import ZDB
import random


class Vdisk:

    def __init__(self, node, zdb, guid=None, data=None):
        self.data = data
        self.node_sal = node
        self.guid = guid
        self.zdb = zdb

    def install(self):
        
        self.disk = self.node_sal.primitives.create_disk(name=self.data['name'],
                                                         zdb=self.zdb,
                                                         mountpoint=self.data['mountPoint'] or None,
                                                         filesystem=self.data['filesystem'] or None,
                                                         size=int(self.data['size']),
                                                         label=self.data['label'])
        self.disk.deploy()

    
    def get_url(self):
        return self.disk.url