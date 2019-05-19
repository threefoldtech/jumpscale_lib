from jumpscale import j

from .CoreDnsThreebot import CorednsThreebot

JSBASE = j.application.jsbase_get_class()


class CorednsThreebotFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.corednsthreebot"
        JSBASE.__init__(self)

    def get(self, name, node, zt_identity=None, nics=None, backplane='backplane', domain=None):
        """
        Get sal for coredns
        Returns:
            the sal layer
        """
        return CorednsThreebot(name, node, zt_identity, nics, backplane, domain)
