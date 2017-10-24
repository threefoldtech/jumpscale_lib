from js9 import j


class Wrappers:

    def sync(self, coro):
        j.logger.get('j.tools.async').warning("j.tools.async.wrappers.sync is deprecated")
        return coro
