from Jumpscale import j
from .GridHealth import GridHealth

JSBASE = j.application.JSBaseClass

class GridHealthFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.tools.gridhealth"
        JSBASE.__init__(self)

    def get(self, node):
        return GridHealth(node)



