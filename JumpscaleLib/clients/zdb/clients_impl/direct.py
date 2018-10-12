from .base import Base


class ZDBClientDirectMode(Base):

    def __init__(self, nsname, addr="localhost", port=9900, secret="123456"):
        super().__init__(addr=addr, port=port, mode="direct", nsname=nsname, secret=secret)

    # No custom logic yet
