from Jumpscale import j
from pprint import pprint 
import os
import struct
import copy
import redis

JSBASE = j.application.JSBaseClass


class ZDBClientNS(JSBASE):

    def __init__(self, zdbclient, nsname):
        """
        is connection to ZDB

        - secret is also the name of the directory where zdb data
          is for this namespace/secret

        config params:
            secret {str} -- is same as namespace id, is a secret to
                            access the data (default: {None})
            port {[int} -- (default: 9900)
            mode -- user,direct,seq(uential) see
                        https://github.com/rivine/0-db/blob/master/README.md
            namespace -- zdb supports namespace
            adminsecret does not have to be set, but when you
            want to create namespaces it is a must

        """
        JSBASE.__init__(self)
        self.zdbclient = zdbclient
        self.redis = j.clients.redis.get(ipaddr=zdbclient.config.data['addr'],
                                         port=zdbclient.config.data['port'],
                                         fromcache=False)

        self.redis = self._patch_redis_client(self.redis)

        self.nsname = nsname.lower().strip()
        self.mode = self.zdbclient.mode

        if self.adminsecret is not "":
            self.redis.execute_command("AUTH", self.adminsecret)

        # put secret on namespace & select namespace
        if self.secret is "":
            self.redis.execute_command("SELECT", self.nsname)
        else:
            self.redis.execute_command("SELECT", self.nsname, self.secret)

    def test(self):
        return self.zdbclient.test()

    @property
    def adminsecret(self):
        return self.zdbclient.adminsecret

    @property
    def secret(self):
        if self.nsname in self.zdbclient.secrets.keys():
            return self.zdbclient.secrets[self.nsname]
        else:
            return self.zdbclient.secrets["default"]

    def _patch_redis_client(self, redis):
        # don't auto parse response for set, it's not 100% redis compatible
        # 0-db does return a key after in set
        if 'SET' in redis.response_callbacks:
            del redis.response_callbacks['SET']
        return redis

    def _key_get(self, key, set=True, iterate=False):

        if self.mode == "seq":
            if key is None:
                key = ""
            else:
                key = struct.pack("<I", key)
        elif self.mode == "direct":
            if set:
                if key not in ["", None]:
                    raise j.exceptions.Input("key need to be None or "
                                             "empty string")
                if key is None:
                    key = ""
            else:
                if key in ["", None]:
                    raise j.exceptions.Input("key cannot be None or "
                                             "empty string")
        elif self.mode == "user":
            if not iterate and key in ["", None]:
                raise j.exceptions.Input("key cannot be None or empty string")
        return key

    def set(self, data, key=None):
        """[summary]

        Arguments:
            data {str or binary} -- the payload can be e.g. capnp binary

        Keyword Arguments:
            key {int} -- when used in sequential mode
                        can be None or int
                        when None it means its a new object,
                        so will be appended

            key {[type]} -- string, only usable for user mode


        """
        key = self._key_get(key, set=True)
        res = self.redis.execute_command("SET", key, data)
        if not res:  # data already present, 0-db did nothing.
            return res

        if self.mode == "seq":
            key = struct.unpack("<I", res)[0]

        return key

    def get(self, key):
        """[summary]

        Keyword Arguments:
            key {int} -- when used in sequential mode
                        can be None or int
                        when None it means its a new object,
                        so will be appended

            key {[type]} -- string, only usable for user mode

            key {[6 byte binary]} -- is binary position is for direct mode

        """
        key = self._key_get(key, set=False)
        return self.redis.execute_command("GET", key)

    def exists(self, key):
        """[summary]

        Arguments:
            key {[type]} - - [description] is id or key
        """
        key = self._key_get(key, set=False)

        return self.redis.execute_command("EXISTS", key) == 1

        # if self.mode=="seq":
        #     id = struct.pack("<I", key)
        #     return self.redis.execute_command("GET", id) is not None
        # elif self.id_enable:
        #     if not j.data.types.int.check(key):
        #         raise j.exceptions.Input("key needs to be int")
        #     pos = self._indexfile.get(key)
        #     if pos == b'':
        #         return False
        #     return self.redis.execute_command("EXISTS", pos)
        # else:
        #     return self.redis.execute_command("EXISTS", pos)

    @property
    def dbtype(self):  # BCDBModel is expecting ZDBClientNS to look like ZDBClient
        return self.zdbclient.dbtype

    @property
    def nsinfo(self):
        res = {}
        cmd = self.redis.execute_command("NSINFO", self.nsname)
        for item in cmd.decode().split("\n"):
            item = item.strip()
            if item == "":
                continue
            if item[0] == "#":
                continue
            if ":" in item:
                key, val = item.split(":")
                try:
                    val = int(val)
                    res[key] = val
                    continue
                except BaseException:
                    pass
                try:
                    val = float(val)
                    res[key] = val
                    continue
                except BaseException:
                    pass
                res[key] = str(val).strip()
        return res

    def list(self, key_start=None, direction="forward", nrrecords=100000,
             result=None):
        if result is None:
            result = []

        def do(arg, result):
            result.append(arg)
            return result

        self.iterate(do, key_start=key_start, direction=direction,
                     nrrecords=nrrecords, _keyonly=True, result=result)
        return result

    def iterate(self, method, key_start=None, direction="forward",
                nrrecords=100000, _keyonly=False, result=None):
        """walk over the data and apply method as follows

        ONLY works for when id_enable is True

        call for each item:
            '''
            for each:
                result = method(id,data,result)
            '''
        result is the result of the previous call to the method

        Arguments:
            method {python method} -- will be called for each item
                                      found in the file

        Keyword Arguments:
            key_start is the start key, if not given will be
                      start of database when direction = forward, else end

        """
        if result is None:
            result = []

        next = self._key_get(key_start, set=False, iterate=True)
        if direction == "forward":
            CMD = "SCANX"
        else:
            CMD = "RSCAN"

        nr = 0
        while nr < nrrecords:
            try:
                if next in [None, ""]:
                    resp = self.redis.execute_command(CMD)
                else:
                    resp = self.redis.execute_command(CMD, next)

                # format of the response
                # - next key to use to continue the scan
                # - array of 3 items [key, size, timestamp]
                next = resp[0]
                keyb = resp[1][0][0]

            except redis.ResponseError as e:
                if e.args[0] == 'No more data':
                    return result

            if self.mode == "seq":
                key_new = struct.unpack("<I", keyb)[0]
            else:
                key_new = keyb

            if _keyonly:
                result = method(key_new, result)
            else:
                data = self.redis.execute_command("GET", keyb)
                result = method(key_new, data, result)

            nr += 1

        return result

    @property
    def count(self):
        i = self.nsinfo
        return i["entries"]

    def test_seq(self):

        nr = self.nsinfo["entries"]
        assert nr == 0
        # do test to see that we can compare
        id = self.set(b"r")
        assert id == 0
        assert self.get(id) == b"r"

        id2 = self.set(b"b")
        assert id2 == 1

        assert self.set(b"r", key=id) is None
        assert self.set(b"rss", key=id) == 0  # changed the data

        nr = self.nsinfo["entries"]
        assert nr == 3

        # test the list function
        assert self.list() == [0, 1]
        assert self.list(1) == []
        assert self.list(0) == [1]

        # TODO:*1
        from IPython import embed
        embed(colors='Linux')
        ss

        pprint(res)

        result = {}

        def test(id, data, result):
            pprint("%s:%s" % (id, data))
            result[id] = data
            return result

        result = self.iterate(test, result={})

        assert self.list(start=newid, end=newid) == [newid]

        result = self.iterate(test, result={}, start=newid, end=newid)

        assert result == {newid: b'r'}

        assert self.exists(newid)

        def dumpdata():

            if self.key_enable:
                inputs = {}
                for i in range(4):
                    data = os.urandom(4096)
                    key = self.set(data, key=str(i))
                    inputs[key] = data

            elif self.id_enable:  # NO LONGER SUPPORTED
                inputs = {}
                for i in range(4):
                    data = os.urandom(4096)
                    key = self.set(data)
                    inputs[key] = data

            for k, expected in inputs.items():
                actual = self.get(k)
                assert expected == actual

        dumpdata()  # is in default namespace

        for i in range(1000):
            nsname = "testns_%s" % i
            exists = self.nsname_exists(nsname)
            if not exists:
                break

        pprint("count:%s" % self.count)

        self.nsname_new(nsname, secret="1234", maxsize=1000, instance=None)

        assert self.nsinfo["data_limits_bytes"] == 1000
        assert self.nsinfo["data_size_bytes"] == 0
        assert self.nsinfo["data_size_mb"] == 0.0
        assert self.nsinfo["entries"] == 0
        assert self.nsinfo["index_size_bytes"] == 0
        assert self.nsinfo["index_size_kb"] == 0.0
        assert self.nsinfo["name"] == nsname
        assert self.nsinfo["password"] == "yes"
        assert self.nsinfo["public"] == "no"

        assert self.nsname == nsname

        # both should be same
        id = self.set(b"a")
        assert self.get(id) == b"a"
        assert self._indexfile.count == 1
        assert self.nsinfo["entries"] == 1

        try:
            dumpdata()
        except Exception as e:
            assert "No space left" in str(e)

        self.nsname_new(nsname + "2", secret="1234", instance=None)

        nritems = 100000
        j.tools.timer.start("zdb")

        pprint("perftest for 100.000 records, should get above 10k per sec")
        for i in range(nritems):
            id = self.set(b"a")

        j.tools.timer.stop(nritems)
