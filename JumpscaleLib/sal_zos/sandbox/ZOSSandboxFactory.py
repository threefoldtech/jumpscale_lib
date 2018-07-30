from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

class ZOSSandboxFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.sandbox"
        JSBASE.__init__(self)

    def get(self, data={}):
        """
        Get sal for influxdb
        
        Arguments:
            object using jumpscale schema
        
        Returns:
            the sal layer 
        """
        return (data)


