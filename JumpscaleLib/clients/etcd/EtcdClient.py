""" A Jumpscale wrapper around the python3 etcd client

    info on etcd client API here:
    https://python-etcd.readthedocs.io/en/latest/
"""

import etcd

TEMPLATE = """
addr = "localhost"
port = "2379"
secrets_ = ""
"""

class EtcdClient:

    __jsbase__ = 'j.tools.configmanager._base_class_config'
    _template = TEMPLATE
    dbtype = 'ETCD'

    def __init__(self, instance, data={}, parent=None, interactive=False,
                                 started=True):
        self._etcd = None
        print ("EtcdClient", instance)
        self.namespaces = {}
        self.EtcdClientNS = self._jsbase(('EtcdClientNS', '.EtcdClientNS'))

    @property
    def secrets(self):
        res={}
        if "," in self.config.data["secrets_"]:
            items = self.config.data["secrets_"].split(",")
            for item in items:
                if item.strip()=="":
                    continue
                nsname,secret = item.split(":")
                res[nsname.lower().strip()]=secret.strip()
        else:
            res["default"]=self.config.data["secrets_"].strip()
        return res

    def namespace_exists(self, name):
        return name in self.namespaces

    def namespace_del(self, name):
        ns = self.namespaces[name]
        try:
            ns.delete_all()
        except KeyError:
            pass
        self.namespaces.pop(name)
        del ns

    def namespace_get(self, name, *args, **kwargs):
        if not name in self.namespaces:
            self.namespaces[name] = self.EtcdClientNS(self, name)
        return self.namespaces[name]

    @property
    def namespace_system(self):
        return self.namespace_get("default")

    def namespace_new(self, name, secret="", maxsize=0, die=False):
        if self.namespace_exists(name):
            if die:
                raise RuntimeError("namespace already exists:%s" % name)
            return self.namespace_get(name)

        #if secret is "" and "default" in self.secrets.keys():
        #    secret = self.secrets["default"]

        return self.namespace_get(name)

    def __str__(self):
        return "etcd:%-14s %-25s:%-4s" % (
            self.instance, self.config.data["addr"],
            self.config.data["port"]
            )

    __repr__ = __str__


