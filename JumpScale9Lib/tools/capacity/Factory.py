from js9 import j

from .capacity_parser import CapacityParser
from .reservation_parser import ReservationParser
from .reality_parser import RealityParser

JSBASE = j.application.jsbase_get_class()


class Factory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.capacity"
        JSBASE.__init__(self)
        self.parser = CapacityParser()
        self.reservation_parser = ReservationParser()
        self.reality_parser = RealityParser()
