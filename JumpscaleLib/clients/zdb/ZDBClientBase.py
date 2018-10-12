
from Jumpscale import j
from .ZDBMeta import ZDBMeta

JSBASE = j.application.JSBaseClass


class ZDBClientBase(JSBASE):

    def __init__(self, addr="localhost", port=9900, mode="seq", secret="", nsname="default"):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        JSBASE.__init__(self)
        self.addr = addr
        self.port = int(port)
        self.mode = mode
        self.secret = secret
        self.type = "ZDB"

        self.redis = _patch_redis_client(j.clients.redis.get(ipaddr=addr, port=port, fromcache=False))

        self.nsname = nsname.lower().strip()

        self.logger_enable()

        if secret != "" and nsname == "default":
            self.logger.debug("AUTH %s" % (self.nsname))
            # self.logger.debug("AUTH %s (%s)"%(self.nsname,self.secret))
            self.redis.execute_command("AUTH", self.secret)

        if self.nsname != "default":
            if self.secret is "":
                self.logger.debug("select namespace:%s with NO secret" % (self.nsname))
                self.redis.execute_command("SELECT", self.nsname)
            else:
                self.logger.debug("select namespace:%s with a secret" % (self.nsname))
                self.redis.execute_command("SELECT", self.nsname, self.secret)

            self.meta = ZDBMeta(self)

    def ping(self):
        """
        go to default namespace & ping
        :return:
        """
        return self.redis.ping()


def _patch_redis_client(redis):
    # don't auto parse response for set, it's not 100% redis compatible
    # 0-db does return a key after in set
    for cmd in ['SET', 'DEL']:
        if cmd in redis.response_callbacks:
            del redis.response_callbacks[cmd]
    return redis
