from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class SandboxPython(JSBASE):
    """
    sandbox python
    """

    def __init__(self):
        JSBASE.__init__(self)
        import jumpscale
        self.JUMPSCALEFILE = jumpscale.__file__

    @property
    def BUILDDIR(self):
        return j.tools.prefab.local.runtimes.python.BUILDDIRL

    @property
    def CODEDIR(self):
        return j.tools.prefab.local.runtimes.python.CODEDIRL

    @property
    def PACKAGEDIR(self):
        return j.dirs.BUILDDIR + "/sandbox/python3/"

    def build(self, jumpscale_branch='development', include_jumpscale=True, reset=False):
        """
        builds python and returns the build dir
        """
        path = j.tools.prefab.local.runtimes.python.build(reset=reset, jumpscale_branch=jumpscale_branch, include_jumpscale=include_jumpscale)
        return path

    def do(self, path="", dest="", build=True, reset=False):
        """
        js_shell 'j.tools.sandboxer.python.do()'

        if dest == "" will be j.dirs.BUILDDIR+"/sandbox/python3/"

        """

        j.tools.prefab.local.system.package.install("zip")

        if build:
            path = self.build(reset=reset)

        if path == "":
            path = self.BUILDDIR

        if not j.sal.fs.exists("%s/bin/python3.6" % path):
            raise RuntimeError(
                "am not in compiled python dir, need to find %s/bin/python3.6" % path)

        if dest == "":
            dest = self.PACKAGEDIR

        j.sal.fs.remove(dest)
        j.sal.fs.createDir(dest)

        for item in ["bin", "include", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        for item in ["pip3", "python3.6", "ipython"]:
            src0 = "%s/bin/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            j.sal.fs.copyFile(src0, dest0)

        j.sal.fs.copyDirTree(j.dirs.BINDIR, j.sal.fs.joinPaths(dest, 'bin'), rsyncdelete=False)

        def dircheck(name):
            for item in ["lib2to3", "idle", ".dist-info", "__pycache__", "site-packages"]:
                if name.find(item) is not -1:
                    return False
            return True

        def binarycheck(path):
            if "parso" in path:
                return True
            files = j.sal.fs.listFilesInDir(path, recursive=True, filter="*.so", followSymlinks=True)
            if len(files) > 0:
                self.logger.debug("found binary files in:%s" % path)
                return True
            return False

        # ignore files which are not relevant,

        ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test"]
        ignorefiles = ['.egg-info', ".pyc"]

        src = "%s/lib/python3.6/site-packages" % (path)
        for ddir in j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True):
            if dircheck(ddir):
                src0 = src+"/%s" % ddir
                if binarycheck(src0):
                    dest0 = "%s/lib/pythonbin/%s" % (dest, ddir)
                else:
                    dest0 = "%s/lib/python/%s" % (dest, ddir)
                self.logger.debug("copy lib:%s ->%s" % (src0, dest0))
                j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)

        src = "%s/lib/python3.6" % (path)
        for ddir in j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True):
            if dircheck(ddir):
                src0 = src+"/%s" % ddir
                if binarycheck(src0):
                    dest0 = "%s/lib/pythonbin/%s" % (dest, ddir)
                else:
                    dest0 = "%s/lib/python/%s" % (dest, ddir)
                self.logger.debug("copy lib:%s ->%s" % (src0, dest0))
                self.logger.debug("copy %s %s" % (src0, dest0))
                j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)

        for item in j.sal.fs.listFilesInDir(src, recursive=False, filter="*.py", exclude=ignorefiles, followSymlinks=True):
            fname = j.sal.fs.getBaseName(item)
            dest0 = "%s/lib/python/%s" % (dest, fname)
            self.logger.debug("copy %s %s" % (item, dest0))
            j.sal.fs.copyFile(item, dest0)

        for item in j.sal.fs.listFilesInDir("%s/lib/python3.6/site-packages" % (path), recursive=False, exclude=ignorefiles, followSymlinks=True):

            fname = j.sal.fs.getBaseName(item)
            if fname.endswith(".so"):
                dest0 = "%s/lib/pythonbin/%s" % (dest, fname)
            else:
                dest0 = "%s/lib/python/%s" % (dest, fname)
            self.logger.debug("copy %s %s" % (item, dest0))
            j.sal.fs.copyFile(item, dest0)

        remove = ["codecs_jp", "codecs_hk", "codecs_cn", "codecs_kr", "testcapi", "tkinter", "audio"]

        # remove some stuff we don't need
        for item in j.sal.fs.listFilesInDir("%s/lib" % (dest), recursive=True):
            if item.endswith(".c") or item.endswith(".h") or item.endswith(".pyc"):
                j.sal.fs.remove(item)
                pass
            for x in remove:
                if item.find(x) is not -1:
                    j.sal.fs.remove(item)
                    pass

        j.tools.sandboxer.python.jumpscale_add()

        self._zip(dest=dest)

        j.tools.sandboxer.libs_sandbox("%s/bin" % self.PACKAGEDIR, "%s/lib", True)
        j.tools.sandboxer.libs_sandbox("%s/lib" % self.PACKAGEDIR, "%s/lib", True)

        print("to test do:")
        print("'cd %s;source env.sh;jumpscale" % self.PACKAGEDIR)

    def _zip(self, dest=""):
        if dest == "":
            dest = j.dirs.BUILDDIR + "/sandbox/python3/"
        cmd = "cd %s;rm -f ../js_sandbox.tar.gz;tar -czf ../js_sandbox.tar.gz .;" % dest
        j.sal.process.execute(cmd)


    def jumpscale_add(self, dest=""):
        """
        js_shell 'j.tools.sandboxer.python.jumpscale_add()'
        """

        def process(c):
            out = ""
            for line in c.split("\n"):
                if line.startswith("#!"):
                    out += "#! /usr/bin/env python3.6\n"
                    continue
                out += "%s\n" % line
            return out

        if dest == "":
            dest = self.PACKAGEDIR

        ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test"]
        ignorefiles = ['.egg-info', ".pyc"]

        for key, p in j.core.state.config_js["plugins"].items():
            dest0 = "%s/lib/jumpscale/%s" % (dest, key)
            j.sal.fs.copyDirTree(p, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)

            if key in ("Jumpscale", "ZeroRobot"):
                jscodedir = "/".join(p.rstrip("/").split("/")[:-1])
                cmds_dir = "{}/cmds".format(jscodedir) if key == "Jumpscale" else "{}/cmd".format(jscodedir)

                for item in j.sal.fs.listFilesInDir(cmds_dir):
                    fname = j.sal.fs.getBaseName(item)
                    dest0 = "%s/bin/%s" % (dest, fname)
                    C = j.sal.fs.readFile(item)
                    C = process(C)
                    j.sal.fs.writeFile(dest0, C)
                    j.sal.fs.chmod(dest0, 0o770)

            if key == 'JumpscalePrefab':
                j.sal.fs.copyDirTree(j.sal.fs.getParent(p), '%s/lib/jumpscale' % dest)
        j.sal.fs.touch("%s/lib/jumpscale/__init__.py" % (dest))

        # SANDBOX APPS
        j.sal.fs.copyDirTree(j.dirs.JSAPPSDIR, dest + j.dirs.JSAPPSDIR)

        # COPY jumpscale.TOML FOR PORTAL CONFIG
        config_dir = dest + '/root/jumpscale/cfg'
        j.sal.fs.createDir(config_dir)
        j.sal.fs.copyFile(j.core.state.configJSPath, '%s/jumpscale.toml' % config_dir)

        # Copy startup configuration

        startup_file = j.dirs.JSAPPSDIR + '/0-robot-portal/autostart/startup.toml'
        if j.sal.fs.exists(startup_file):
            j.sal.fs.copyFile(startup_file, '%s/.startup.toml' % dest)

        j.sal.fs.copyFile(self.JUMPSCALEFILE, "%s/lib/jumpscale/jumpscale.py" % (dest))

        self.env_write(dest)

    def env_write(self, dest=""):
        """
        js_shell 'j.tools.sandboxer.python.env_write()'
        """

        if dest == "":
            dest = self.PACKAGEDIR

        C = """
        export PBASE=`pwd`

        export PATH=$PBASE/bin:/bin:/usr/local/bin:/usr/bin:$PATH
        export PYTHONPATH=$PBASE/lib/python:$PBASE/lib/pythonbin:$PBASE/lib/python.zip:$PBASE/lib/jumpscale:$PBASE/lib/pythonbin/lib-dynload:$PBASE/bin
        export PYTHONHOME=$PBASE

        export LIBRARY_PATH="$PBASE/bin:$PBASE/lib"
        export LD_LIBRARY_PATH="$LIBRARY_PATH"

        export LDFLAGS="-L$LIBRARY_PATH/"

        export LC_ALL=C.UTF-8
        export LANG=C.UTF-8

        export HOME=$PBASE/root

        export PS1="JUMPSCALE: "

        """
        j.sal.fs.writeFile("%s/env.sh" % dest, j.data.text.strip(C))
        # make sure to make the env.sh file executable
        j.sal.process.execute('chmod +x %s/env.sh' % dest)


        print("to test:\ncd %s;source env.sh" % dest)

    def upload(self):
        """
        """
        if self.core.isMac:
            cmd = "cd %s/sandbox;scp -P 1022 js_sandbox.zip root@download.gig.tech:data/js_sandbox_osx.zip" % j.dirs.BUILDDIR
        else:
            cmd = "cd %s/sandbox;scp -P 1022 js_sandbox.zip root@download.gig.tech:data/js_sandbox_linux64.zip" % j.dirs.BUILDDIR
