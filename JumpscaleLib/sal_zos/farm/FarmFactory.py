from jumpscale import j

JSBASE = j.application.jsbase_get_class()

from .Farm import Farm

class FarmFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.farm"
        JSBASE.__init__(self)

    def get(self, farmer_iyo_org):
        """
        Get sal for etcd management in ZOS
        
        Arguments:
            farmer_iyo_org: the farmer iyo organisation
        
        Returns:
            the sal layer 
        """
        return Farm(farmer_iyo_org)