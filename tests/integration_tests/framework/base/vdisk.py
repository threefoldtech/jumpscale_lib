from jumpscale import j
from framework.base.zdb import ZDB
import random


class Vdisk:

    def __init__(self, node, guid=None, data=None, zdb=None):
        self.data = data
        self.node_sal = node
        self.guid = guid
        self.zdb = zdb
    def install(self):
        zdb = self.zdb or self.create_zdb()
        self.disk = self.node_sal.primitives.create_disk(name=self.data['name'],
                                                         zdb=zdb,
                                                         mountpoint=self.data['mountPoint'] or None,
                                                         filesystem=self.data['filesystem'] or None,
                                                         size=int(self.data['size']),
                                                         label=self.data['label'])
        self.disk.deploy()

    def create_zdb(self):
        zdb_data = {'name': j.data.idgenerator.generateXCharID(10),
                    'nodePort': random.randint(600, 1000),
                    'mode': 'user',
                    'sync': False,
                    'admin': '',
                    'path': self.data["path"],
                    'namespaces': [],
                    'ztIdentity': '',
                    'nics': [],
                    'diskType': self.data["diskType"],
                    'size': self.data["size"]
                    }
        self.zdb_obj = ZDB(node=self.node_sal, data=zdb_data)
        self.zdb = self.zdb_obj._zerodb_sal
        return self.zdb
