from Jumpscale import j
JSBASE = j.application.JSBaseClass

from .ZStor import ZeroStor


class ZeroStorFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.zstor"
        JSBASE.__init__(self)

    def get(self, name, container, bind='0.0.0.0:8080', data_dir='/mnt/data',
            meta_dir='/mnt/metadata', max_size_msg=64):
        """
        Get sal for zero stor in ZOS
        Returns:
            the sal layer 
        """
        return ZeroStor(name, container, bind=bind, data_dir=data_dir,
                        meta_dir=meta_dir, max_size_msg=max_size_msg)
