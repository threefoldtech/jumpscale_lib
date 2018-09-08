""" A Jumpscale wrapper around the python3 etcd-v3 client
    https://github.com/kragniz/python-etcd3

    the etcd v2 APIs cannot cope with binary key/value data.
    the etcd v3 API can

    CAVEAT: this particular python-etcd-v3 client cannot
    distinguish between keys with a prefix using "/" as
    separators.  therefore, in e.g. BCDBModel.py it was
    necessary to put data under the prefix "bcdb" and
    the unique index reference under "_bcdb".
"""

import etcd3
import base64
import zlib

from etcd3.exceptions import Etcd3Exception

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

            self._etcd = etcd3.client(host=addr, port=port)

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
        v = value
        #if value is not None:
        #    v = zlib.compress(value)
        #    v = base64.encodebytes(v)
        #else:
        #    v = None
        #print ("set", name, repr(v))
        self.etcd.put(self._key_to_etcd(name), v)

    def get(self, name):
        etckey = self._key_to_etcd(name)
        try:
            r = self.etcd.get(etckey)
        except Etcd3Exception as e:
            raise KeyError(e)

        #print ("get", name, etckey, repr(r))
        if r[1] is None:
            raise KeyError('etcd key not found %s' % repr(etckey))
        return r[0]
        value = r.value
        #value = base64.decodebytes(r.value.encode())
        #value = zlib.decompress(value)
        #print ("get", name, value)
        return value

    def incr(self, name, amount=1):
        try:
            r = self.get(name)
            if r is None or r == '':
                value = amount
            else:
                value = int(r) + amount
        except KeyError:
            value = amount
        self.set(name, str(value).encode())
        return value

    def delete(self, key):
        try:
            res = self.etcd.delete(self._key_to_etcd(key))
        except Etcd3Exception as e:
            raise KeyError(e)
        if not res:
            raise KeyError(key)

    def delete_all(self):
        try:
            res = self.etcd.delete_prefix(self._key_to_etcd(''))
        except Etcd3Exception as e:
            raise KeyError(e)
        if not res:
            raise KeyError(key)

    def keys(self, pattern=""):
        res = []
        try:
            getp = self._key_to_etcd(pattern)
            #print ("keys", getp)
            r = self.etcd.get_prefix(getp)
        except Etcd3Exception:
            return res
        if pattern:
            l = len(pattern)+1
            #print ("pattern", pattern, l)
        else:
            l = 0
        for child in r:
            #print("child %s:" % repr(child))
            key = child[1].key.decode()
            res.append(self._etcd_to_key(key)[l:])
        return res

    def __str__(self):
        return "%s: ns:%s" % (str(self.dbclient), self.nsname)

    __repr__ = __str__
