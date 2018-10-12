from Jumpscale import j
import struct
import redis

from .ZDBClientBase import ZDBClientBase

class ZDBClient(ZDBClientBase):

    def __init__(self, nsname, addr="localhost",port=9900,mode="seq",secret="123456"):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        ZDBClientBase.__init__(self,addr=addr,port=port,mode=mode,nsname=nsname ,secret=secret)


    def test(self):
        return self.test_seq()

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
        key1 = self._key_get(key)
        # print("key:%s"%key1)
        # print(data[:100])
        res = self.redis.execute_command("SET", key1, data)
        if not res:  # data already present, 0-db did nothing.
            return res
        # print(res)
        if self.mode == "seq":
            key = struct.unpack("<I", res)[0]

        return key

    def delete(self, key):
        key1 = self._key_get(key)
        res = self.redis.execute_command("DEL", key1)
        # if not res:  # data already present, 0-db did nothing.
        #     return res
        # # print(res)
        # if self.mode == "seq":
        #     key = struct.unpack("<I", res)[0]
        #
        # return key

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
    def dbtype(self):  # BCDBModel is expecting ZDBClient to look like ZDBClient
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

    def list(self, key_start=None, direction="forward", nrrecords=100000, result=None):
        if result is None:
            result = []

        def do(arg, result):
            result.append(arg)
            return result

        self.iterate(do, key_start=key_start, direction=direction,
                     nrrecords=nrrecords, _keyonly=True, result=result)
        return result

    def iterate(self, method, key_start=None, direction="forward",nrrecords=100000, _keyonly=False, result=None):
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

        nr = 0

        if key_start is not None:
            next = self.redis.execute_command("KEYCUR", self._key_get(key_start))
            if _keyonly:
                result = method(key_start, result)
            else:
                data = self.redis.execute_command("GET", self._key_get(key_start))
                result = method(key_start, data, result)
            nr += 1
        else:
            next = None

        if direction == "forward":
            CMD = "SCANX"
        else:
            CMD = "RSCAN"

        while nr < nrrecords:
            try:
                if next in [None, ""]:
                    resp = self.redis.execute_command(CMD)
                else:
                    resp = self.redis.execute_command(CMD, next)

                # format of the response
                # see https://github.com/threefoldtech/0-db/tree/development#scan

            except redis.ResponseError as e:
                if e.args[0] == 'No more data':
                    return result
                j.shell()
                raise e

            (next, res) = resp

            if len(res) > 0:
                for item in res:
                    # there can be more than 1

                    keyb, size, epoch = item

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
            else:
                j.shell()
                w

        return result

    @property
    def count(self):
        i = self.nsinfo
        return i["entries"]

