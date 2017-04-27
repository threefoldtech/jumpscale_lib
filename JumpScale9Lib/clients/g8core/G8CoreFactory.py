from JumpScale9 import j
# try:
#     import g8core
# except BaseException:
#     path = j.clients.git.getContentPathFromURLorPath("https://github.com/g8os/core0/tree/1.1.0-alpha/pyclient")
#     j.do.execute("cd %s;python3 setup.py install" % path)
#     import g8core
import g8core


class G8CoreFactory():

    def __init__(self):
        self.__jslocation__ = "j.clients.g8core"
        self.__imports__ = g8core

    def install(self):
        path = j.clients.git.getContentPathFromURLorPath("https://github.com/g8os/core0/tree/1.1.0-alpha/pyclient")
        j.do.execute("cd %s;python3 setup.py install" % path)

    def get(self, host, port=6379, password=''):
        return g8core.Client(host=host, port=port, password=password)
