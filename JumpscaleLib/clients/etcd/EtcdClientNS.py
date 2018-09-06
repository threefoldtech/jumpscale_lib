""" A Jumpscale wrapper around the python3 etcd client

    info on etcd client API here:
    https://python-etcd.readthedocs.io/en/latest/
"""

import etcd
import base64
import zlib

class EtcdClientNS:

    def __init__(self, dbclient, nsname):
        self._etcd = None
        self.dbclient = dbclient
        self.nsname = nsname.lower().strip()
        #print ("EtcdClient", dbclient)

    @property
    def secret(self):
        if self.nsname in self.dbclient.secrets.keys():
            return self.dbclient.secrets[self.nsname]
        else:
            return self.dbclient.secrets["default"]

    @property
    def dbtype(self):
        return self.dbclient.dbtype

    @property
    def etcd(self):
        if self._etcd is None:
            d = self.dbclient.config.data
            addr = d["addr"]
            port = int(d["port"])

            self._etcd = etcd.Client(host=addr, port=port)

        return self._etcd

    def _etcd_to_key(self, key):
        """ reverse of _key_to_etcd
        """
        prefix = "/%s/%s/" % (self.dbclient.instance, self.nsname)
        plen = len(prefix)
        assert key[:plen] == prefix, "key %s wrong namespace %s" % (key, prefix)
        #print ("_etcd_to_key", key, key[plen])
        return key[plen:]

    def _key_to_etcd(self, pattern):
        """ turns a key into an appropriate pattern for etcd, which,
            according to the API docs, needs "/" to separate hierarchical
            namespaces (like directories).

            an arbitrary decision is made to use the name of the instance
            (taken from the config) to create separate namespaces.
        """
        #pattern = pattern.replace(':', '/')
        res = "/%s/%s" % (self.dbclient.instance, self.nsname)
        if pattern:
            res = "%s/%s" % (res, pattern)
        return res

    def set(self, name, value):
        if value is not None:
            v = zlib.compress(value)
            v = base64.encodestring(v)
        else:
            v = None
        #print ("set", name, repr(v))
        self.etcd.write(self._key_to_etcd(name), v)

    def get(self, name, wait=False):
        etckey = self._key_to_etcd(name)
        try:
            r = self.etcd.read(etckey, wait=wait)
        except etcd.EtcdKeyNotFound as e:
            raise KeyError(e)
        #print ("get", name, etckey, repr(r.value))
        if r.value is None:
            return None
        value = base64.decodestring(r.value.encode())
        value = zlib.decompress(value)
        #print ("get", name, value)
        return value

    def incr(self, name, amount=1):
        try:
            r = self.get(name)
            value = int(r) + amount
        except etcd.EtcdKeyNotFound:
            value = amount
        self.set(name, str(value).encode())
        return value

    def delete_all(self):
        try:
            self.etcd.delete(self._key_to_etcd(''), recursive=True)
        except etcd.EtcdKeyNotFound:
            pass

    def keys(self, pattern=""):
        res = []
        try:
            r = self.etcd.read(self._key_to_etcd(pattern))
        except etcd.EtcdKeyNotFound:
            return res
        if r.children is None:
            return res
        for child in r.children:
            #print("child %s: %s" % (child.key, child.value))
            res.append(self._etcd_to_key(child.key)[len(pattern)+1:])
        return res

    def __str__(self):
        return "%s: ns:%s" % (str(self.dbclient), self.nsname)

    __repr__ = __str__
