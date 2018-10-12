
from Jumpscale import j

from .ZDBClient import ZDBClient
from .ZDBClientBase import ZDBClientBase


class ZDBAdminClient(ZDBClientBase):


    def __init__(self, addr="localhost",port=9900,mode="seq",secret="123456"):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        ZDBClientBase.__init__(self,addr=addr,port=port,mode=mode,secret=secret)
        self._system = None

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
            self._system = ZDBClient("system",secret=self.secret)
        return self._system

    def namespace_new(self, name, secret="", maxsize=0, die=False):
        if self.namespace_exists(name):
            if die:
                raise RuntimeError("namespace already exists:%s" % name)
            return self.namespace_get(name)

        self.redis.execute_command("NSNEW", name)
        if secret is not "":
            self.redis.execute_command("NSSET", name, "password", secret)
            self.redis.execute_command("NSSET", name, "public", "no")
        self.logger.debug("namespace:%s NEW" % name)

        if maxsize is not 0:
            self.redis.execute_command("NSSET", name, "maxsize", maxsize)

        ns=ZDBClient(addr=self.addr,port=self.port,mode=self.mode,secret=self.secret,nsname="system")
        ns.meta


    def namespace_delete(self, name):
        if self.namespace_exists(name):
            self.redis.execute_command("NSDEL", name)

    def reset(self,ignore=[]):
        """
        dangerous, will remove all namespaces & all data
        :param: list of namespace names not to reset
        :return:
        """
        for name in self.namespaces_list():
            if name not in ["default"] and name not in ignore:
                self.namespace_delete(name)

        if "system" not in ignore:
            self.namespace_new("system",secret=self.secret)
