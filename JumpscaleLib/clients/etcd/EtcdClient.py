""" A Jumpscale wrapper around the python3 etcd client

    info on etcd client API here:
    https://python-etcd.readthedocs.io/en/latest/
"""

import etcd

TEMPLATE = """
addr = "localhost"
port = "2379"
"""

def key_to_etcd(pattern):
    pattern = pattern.replace(':', '/')
    return "/" + pattern

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

    def _set(self, pattern, val):
        return self.etcd.write(key_to_etcd(pattern), val)

    def _get(self, pattern):
        return self.etcd.read(key_to_etcd(pattern))

    def incr(self, name, amount=1):
        try:
            r = self._get(name)
            value = int(r.value)
        except etcd.EtcdKeyNotFound:
            value = amount
        self._set(name, str(value))
        return value

    def keys(self, pattern=""):
        res = []
        try:
            r = self._get(pattern)
        except etcd.EtcdKeyNotFound:
            return res
        for child in r.children:
            print("%s: %s" % (child.key, child.value))
            res.append(child.key)
        return res

    def __str__(self):
        return "etcd:%-14s %-25s:%-4s" % (
            self.instance, self.config.data["addr"],
            self.config.data["port"]
            )

    __repr__ = __str__
