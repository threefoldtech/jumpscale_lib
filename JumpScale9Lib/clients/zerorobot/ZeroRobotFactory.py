from zerorobot.dsl.ZeroRobotClient import ZeroRobotClient
from JumpScale9.core.State import ClientConfig

from js9 import j

CACHE_KEY = 'zerorobot'


class ZeroRobotFactory:

    _cache = {}

    def __init__(self):
        self.__jslocation__ = "j.clients.zrobot"

    def get(self, base_url):
        """
        Get a ZeroRobot client for base_url.
        if it exists a client for this base_url loaded in memory, return it.
        otherwise, create a new client, put it in the cache and then return it
        """
        if base_url not in self._cache:
            self._cache[base_url] = ZeroRobotClient(base_url)
        return self._cache[base_url]

    def get_by_key(self, key):
        if key in self._cache:
            return self._cache[key]

        cfg = j.core.state.clientConfigGet(CACHE_KEY, key)
        if not cfg.data:
            raise KeyError("no zero-robot client found for key %s" % key)

        client = self.get(cfg.data['base_url'])
        self.set(key, client)
        return client

    def set(self, key, client):
        """
        associate key with an instance of client
        """
        cfg = ClientConfig(CACHE_KEY, key)
        cfg.data = {'base_url': client._client.api.base_url}
        cfg.save()
        self._cache[key] = client
