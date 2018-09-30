from jumpscale import j

TEMPLATE = """
addr = "127.0.0.1"
port = 9900
adminsecret_ = ""
secrets_ = ""
mode = "user"
"""

JSConfigBase = j.tools.configmanager.base_class_config


class ZdbConfig(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, interactive=interactive)
        self._zdb = None

    @property
    def zdb(self):
        if self._zdb is None:
            d = self.config.data
            addr = d["addr"]
            port = d["port"]
            adminsecret = d["adminsecret_"]
            secrets = d["secrets_"]
            mode = d["mode"]

            self._zdb = j.clients.zdb.get(
                addr=addr, port=port, adminsecret=adminsecret, secrets=secrets, mode=mode)
        return self._zdb

    def __str__(self):
        return "redis:%-14s %-25s:%-4s (ssl:%s)" % (self.instance, self.config.data["addr"],  self.config.data["port"], self.config.data["ssl"])

    __repr__ = __str__
