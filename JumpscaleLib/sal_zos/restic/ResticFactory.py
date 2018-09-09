from .Restic import Restic
from Jumpscale import j

JSBASE = j.application.jsbase_get_class()


class ResticFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.restic"
        JSBASE.__init__(self)

    @staticmethod
    def get(container, repo):
        """
        Get sal for restic
        Returns:
            the sal layer
        """
        return Restic(container, repo)
