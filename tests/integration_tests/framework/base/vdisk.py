from jumpscale import j
from zerorobot.service_collection import ServiceNotFoundError
from zdb import ZDB
import random


class Vdisk:

    def __init__(self, node, guid=None, data=None, zdb=None):
        self.data = data
        self.node_sal = node
        self.guid = guid
        self.zdb = zdb or self.create_zdb()

    def install(self):
        self.disk = self.node_sal.primitives.create_disk(name=self.data['name'],
                                                         zdb=self.zdb,
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
        self.zdb = ZDB(self.node_sal, zdb_data)

        return self.zdb
