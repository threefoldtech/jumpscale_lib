from .base import Base


class ZDBClientUserMode(Base):

    def __init__(self, nsname, addr="localhost", port=9900, secret="123456"):
        super().__init__(addr=addr, port=port, mode="user", nsname=nsname, secret=secret)

    def set(self, data, key):
        return self.redis.execute_command("SET", key, data)
