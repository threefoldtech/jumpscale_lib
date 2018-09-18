from Jumpscale import j


class Rexplorer(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.tools.rexplorer"
        JSBASE.__init__(self)

    def install(self):
        """
        use prefab to install rexplorer & get it started
        :return:
        """
        j.shell()
