from js9 import j

from .parser import CapacityParser

JSBASE = j.application.jsbase_get_class()


class Factory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.capacity"
        JSBASE.__init__(self)
        self.parser = CapacityParser()
