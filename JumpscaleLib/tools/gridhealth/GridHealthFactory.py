from Jumpscale import j
from .GridHealth import GridHealth, GridHealthQuery

JSBASE = j.application.JSBaseClass

class GridHealthFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.tools.gridhealth"
        JSBASE.__init__(self)

    def get(self, node=None, robot=None):
        if node is None and robot is None:
            return GridHealthQuery()

        return GridHealth(node, robot)



