
from Jumpscale import j

from .ZDBClientBase import ZDBClientBase


class ZDBAdminClient(ZDBClientBase):

    def __init__(self, addr="localhost", port=9900, mode="seq", secret="123456"):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        ZDBClientBase.__init__(self, addr=addr, port=port, mode=mode, secret=secret)
        self._system = None
        self.logger_enable()

    @property
    def meta(self):
        cl = j.clients.zdb.client_get(self.nsname, secret=self.secret, mode=self.mode)
        return cl.meta

    def namespace_exists(self, name):
        try:
            self.redis.execute_command("NSINFO", name)
            return True
        except Exception as e:
            if not "Namespace not found" in str(e):
                raise RuntimeError("could not check namespace:%s, error:%s" % (name, e))
            return False

    def namespaces_list(self):
        res = self.redis.execute_command("NSLIST")
        return [i.decode() for i in res]

    @property
    def namespace_system(self):
        if self._system is None:
            self._system = j.clients.zdb.client_get("system", secret=self.secret, mode=self.mode)
        return self._system

    def namespace_new(self, name, secret="", maxsize=0, die=False):
        self.logger.debug("namespace_new:%s" % name)
        if self.namespace_exists(name):
            self.logger.debug("namespace exists")
            if die:
                raise RuntimeError("namespace already exists:%s" % name)
            return j.clients.zdb.client_get(addr=self.addr, port=self.port, mode=self.mode, secret=secret, nsname=name)

        self.redis.execute_command("NSNEW", name)
        if secret is not "":
            self.logger.debug("set secret")
            self.redis.execute_command("NSSET", name, "password", secret)
            self.redis.execute_command("NSSET", name, "public", "no")

        if maxsize is not 0:
            self.logger.debug("set maxsize")
            self.redis.execute_command("NSSET", name, "maxsize", maxsize)

        self.logger.debug("connect client")
        if not self.namespace_exists("system"):
            self.namespace_new("system", self.secret)  # create new one with adminsecret

        ns = j.clients.zdb.client_get(addr=self.addr, port=self.port, mode=self.mode, secret=self.secret, nsname="system")
        ns.meta

        ns = j.clients.zdb.client_get(addr=self.addr, port=self.port, mode=self.mode, secret=secret, nsname=name)
        ns.meta

        assert ns.ping()

        return ns

    def namespace_delete(self, name):
        if self.namespace_exists(name):
            self.redis.execute_command("NSDEL", name)

    def reset(self, ignore=[]):
        """
        dangerous, will remove all namespaces & all data
        :param: list of namespace names not to reset
        :return:
        """
        for name in self.namespaces_list():
            if name not in ["default"] and name not in ignore:
                self.namespace_delete(name)

        if "system" not in ignore:
            self.namespace_new("system", secret=self.secret)
