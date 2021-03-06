from .stats_collector import StatsCollector
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class StatsCollectorFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.stats_collector"
        JSBASE.__init__(self)

    @staticmethod
    def get(container, ip, port, db, retention, jwt):
        """
        Get sal for Disks
        Returns:
            the sal layer 
        """
        return StatsCollector(container, ip, port, db, retention, jwt)
