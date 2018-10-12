from Jumpscale import j
import struct
import redis

from ..ZDBClientBase import ZDBClientBase


class Base(ZDBClientBase):

    def __init__(self, nsname, mode, addr="localhost", port=9900, secret="123456"):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        ZDBClientBase.__init__(self, addr=addr, port=port, mode=mode, nsname=nsname, secret=secret)

    def _key_encode(self, key):
        return key

    def _key_decode(self, key):
        return key

    def set(self, data):
        return self.redis.execute_command("SET", '', data)

    def get(self, key):
        return self.redis.execute_command("GET", key)

    def exists(self, key):
        return self.redis.execute_command("EXISTS", key) == 1

    def delete(self, key):
        if not key:
            raise ValueError("key must be provided")
        self.redis.execute_command("DEL", key)

    @property
    def nsinfo(self):
        cmd = self.redis.execute_command("NSINFO", self.nsname)
        return _parse_nsinfo(cmd.decode())

    def list(self, key_start=None, reverse=False):
        """
        list all the keys in the namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                        if False, walk from older to newer keys
                        if True walk from newer to older keys
                        defaults to False
        :param reverse: bool, optional
        :return: list of keys
        :rtype: [str]
        """
        result = []
        for key, data in self.iterate(key_start=key_start, reverse=reverse, keyonly=True):
            result.append(key)
        return result

    def iterate(self, key_start=None, reverse=False, keyonly=False):
        """
        walk over all the namespace and yield (key,data) for each entries in a namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                if False, walk from older to newer keys
                if True walk from newer to older keys
                defaults to False
        :param reverse: bool, optional
        :param keyonly: [description], defaults to False
        :param keyonly: bool, optional
        :raises e: [description]
        """

        next = None
        data = None

        if key_start is not None:
            next = self.redis.execute_command("KEYCUR", self._key_encode(key_start))
            if not keyonly:
                data = self.get(key_start)
            yield (key_start, data)

        CMD = "SCANX" if not reverse else "RSCAN"

        while True:
            try:
                if not next:
                    response = self.redis.execute_command(CMD)
                else:
                    response = self.redis.execute_command(CMD, next)
                # format of the response
                # see https://github.com/threefoldtech/0-db/tree/development#scan
            except redis.ResponseError as e:
                if e.args[0] == 'No more data':
                    return
                raise e

            (next, results) = response
            for item in results:
                keyb, size, epoch = item
                key_new = self._key_decode(keyb)
                data = None
                if not keyonly:
                    data = self.redis.execute_command("GET", keyb)
                yield (key_new, data)

    @property
    def count(self):
        """
        :return: return the number of entries in the namespace
        :rtype: int
        """
        return self.nsinfo['entries']


def _parse_nsinfo(raw):
    def empty(line):
        line = line.strip()
        if len(line) <= 0 or \
                line[0] == "#" or \
                ":" not in line:
            return False
        return True

    info = {}
    for line in filter(empty, raw.splitlines()):
        key, val = line.split(":")
        try:
            val = int(val)
            info[key] = val
            continue
        except ValueError:
            pass
        try:
            val = float(val)
            info[key] = val
            continue
        except ValueError:
            pass

        info[key] = str(val).strip()
    return info
