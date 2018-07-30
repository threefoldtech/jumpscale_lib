from jumpscale import j
# import JumpscaleLib.baselib.remote

JSBASE = j.application.jsbase_get_class()

from .influxdb import InfluxDB

class InfluxDBFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.zos_sal.influx"
        JSBASE.__init__(self)

    def get(self, container, ip, port, rpcport):
        """
        Get sal for InfluxDB
        
        Arguments:
            container, ip, port, rpcport
        
        Returns:
            the sal layer 
        """
        return InfluxDB(container, ip, port, rpcport)


