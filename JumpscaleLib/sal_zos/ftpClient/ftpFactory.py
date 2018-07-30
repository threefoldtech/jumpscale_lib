from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from .FtpClient import FtpClient

class FtpFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.zos_sal.ftpclient"
        JSBASE.__init__(self)

    def get(self, url):
        """
        Get sal for FtpClient
        
        Arguments:
            url
        
        Returns:
            the sal layer 
        """
        return FtpClient(url)


