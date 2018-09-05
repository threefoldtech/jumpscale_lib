""" A Jumpscale wrapper around the python3 etcd client
"""

import etcd

TEMPLATE = """
addr = "localhost"
port = "2379"
"""

class EtcdClient:

    __jsbase__ = 'j.tools.configmanager._base_class_config'
    _template = TEMPLATE
    dbtype = 'ETCD'

    def __init__(self, instance, data={}, parent=None, interactive=False,
                                 started=True):
        self._etcd = None
        print ("EtcdClient", instance)

    @property
    def etcd(self):
        if self._etcd is None:
            d = self.config.data
            addr = d["addr"]
            port = int(d["port"])

            self._etcd = etcd.Client(host=addr, port=port)

        return self._etcd

    def __str__(self):
        return "etcd:%-14s %-25s:%-4s" % (
            self.instance, self.config.data["addr"],
            self.config.data["port"]
            )

    __repr__ = __str__
