from js9 import j

JSBASE = j.application.jsbase_get_class()


class SandboxPython(JSBASE):
    """
    sandbox python
    """

    def __init__(self):
        JSBASE.__init__(self)
        self.builddir = None

    def build(self):
        """
        builds python and returns the build dir
        """
        path = j.tools.prefab.local.runtimes.python.build()
        self.builddir = path
        return path

    def do(self, path="", dest="", build=False):
        """
        js9 'j.tools.sandboxer.python.do()'

        if dest == "" will be j.dirs.BUILDDIR+"/sandbox/python3/"

        """
        if path == "" and build:
            path = self.build()

        if path == "":
            path = j.sal.fs.getcwd()

        if not j.sal.fs.exists("%s/bin/python3.6" % path):
            raise RuntimeError(
                "am not in compiled python dir, need to find %s/bin/python3.6" % path)

        if dest == "":
            dest = j.dirs.BUILDDIR + "/sandbox/python3/"
            j.sal.fs.createDir(dest)

        for item in ["bin", "include", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        # j.sal.fs.copyFile("%s/bin/python3.6"%path,)

        # ignorefiles=['.egg-info',"*test*","*audio*"]
        # bindest = self.replace("$BUILDDIRL/bin")
        # self.prefab.core.copyTree(source=libpath, dest=bindest, keepsymlinks=True, deletefirst=False,
        #                           overwriteFiles=True, recursive=True, rsyncdelete=False, createdir=True,ignorefiles=ignorefiles)
