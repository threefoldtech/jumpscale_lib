from .Farm import Farm
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class FarmFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.farm"
        JSBASE.__init__(self)

    def get(self, farmer_iyo_org):
        """
        Get sal for farm

        Arguments:
            farmer_iyo_org: the farmer iyo organisation

        Returns:
            the sal layer
        """
        return Farm(farmer_iyo_org)
