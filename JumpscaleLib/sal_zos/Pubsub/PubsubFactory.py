from .Pubsub import Pubsub
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class PubsubFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.pubsub"
        JSBASE.__init__(self)

    @staticmethod
    def get(loop, host, port=6379, password="", db=0, ctx=None,
            timeout=None, testConnectionAttempts=3, callback=None):
        """
        Get sal for pubsub
        Returns:
            the sal layer 
        """
        return Pubsub(loop, host, port, password, db, ctx, timeout, testConnectionAttempts, callback)
