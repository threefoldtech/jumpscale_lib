from Jumpscale import j

JSBASE = j.application.JSBaseClass


class SandboxPython(JSBASE):
    """
    sandbox python
    """

    def __init__(self):
        JSBASE.__init__(self)
        import Jumpscale
        self.JUMPSCALEFILE = Jumpscale.__file__
        self.logger_enable()

    @property
    def BUILDDIR(self):
        return j.tools.prefab.local.runtimes.python.BUILDDIRL

    @property
    def CODEDIR(self):
        return j.tools.prefab.local.runtimes.python.CODEDIRL

    @property
    def PACKAGEDIR(self):
        return j.dirs.BUILDDIR + "/sandbox/tfbot/"

    def build(self, jumpscale_branch='development', reset=False):
        """
        builds python and returns the build dir
        """
        path = j.tools.prefab.local.runtimes.python.build(reset=reset,
                            jumpscale_branch=jumpscale_branch, include_jumpscale=True)
        return path

    def do(self, path="", dest="", build=True, reset=False):
        """
        js_shell 'j.tools.sandboxer.python.do(build=True)'

        if dest == "" will be j.dirs.BUILDDIR+"/sandbox/tfbot/"

        """
        self.logger.info("sandbox:%s" % path)
        j.tools.prefab.local.system.package.install("zip")
        if j.core.platformtype.myplatform.isMac:
            j.tools.prefab.local.system.package.install("redis")
        else:
            j.tools.prefab.local.system.package.install("redis-server")

        if build:
            path = self.build(reset=reset)

        if path == "":
            path = self.BUILDDIR

        if not j.sal.fs.exists("%s/bin/python3.6" % path):
            j.shell()
            raise RuntimeError(
                "am not in compiled python dir, need to find %s/bin/python3.6" % path)

        if dest == "":
            dest = self.PACKAGEDIR

        j.sal.fs.remove(dest)
        j.sal.fs.createDir(dest)

        for item in ["bin", "root", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        for item in ["pip3", "python3.6", "ipython","bpython","electrum","pudb3","zrobot"]:
            src0 = "%s/bin/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)

        #for OSX
        for item in ["libpython3.6m.a"]:
            src0 = "%s/lib/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)




        #LINK THE PYTHON BINARIES
        j.sal.fs.symlink("%s/bin/python3.6" % dest, "%s/bin/python" % dest, overwriteTarget=True)
        j.sal.fs.symlink("%s/bin/python3.6" % dest, "%s/bin/python3" % dest, overwriteTarget=True)


        #NOW DEAL WITH THE PYTHON LIBS

        def dircheck(name):
            for item in ["lib2to3", "idle", ".dist-info", "__pycache__", "site-packages"]:
                if name.find(item) is not -1:
                    return False
            return True

        def binarycheck(path):
            """
            checks if there is a .so in the directory (python libs), if so we need to copy to the binary location
            """
            if "parso" in path:
                return True
            if "jedi" in path:
                return True

            files = j.sal.fs.listFilesInDir(path, recursive=True, filter="*.so", followSymlinks=True)
            files += j.sal.fs.listFilesInDir(path, recursive=True, filter="*.so.*", followSymlinks=True)
            if len(files) > 0:
                self.logger.debug("found binary files in:%s" % path)
                return True
            return False

        # ignore files which are not relevant,

        ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test",
                     "electrum_"]
        ignorefiles = ['.egg-info', ".pyc"]

        todo = ["%s/lib/python3.6/site-packages" % path,"%s/lib/python3.6" % path]
        for src in todo:
            for ddir in j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True):
                if dircheck(ddir):
                    src0 = src+"/%s" % ddir
                    if binarycheck(src0):
                        dest0 = "%s/lib/pythonbin/%s" % (dest, ddir)
                    else:
                        dest0 = "%s/lib/python/%s" % (dest, ddir)
                    self.logger.debug("copy lib:%s ->%s" % (src0, dest0))
                    j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)


            for item in j.sal.fs.listFilesInDir(src, recursive=False, exclude=ignorefiles, followSymlinks=True):
                fname = j.sal.fs.getBaseName(item)
                dest0 = ""
                if fname.endswith(".so") or ".so." in fname:
                    dest0 = "%s/lib/pythonbin/%s" % (dest, fname)
                if fname.endswith(".py"):
                    dest0 = "%s/lib/python/%s" % (dest, fname)
                self.logger.debug("copy %s %s" % (item, dest0))
                if dest0 is not "":
                    j.sal.fs.copyFile(item, dest0)

        self.env_write(dest)


        if j.core.platformtype.myplatform.isUbuntu: #only for building
            #no need to sandbox in non linux systems
            j.tools.sandboxer.libs_sandbox("%s/bin" % self.PACKAGEDIR, "%s/lib"% self.PACKAGEDIR, True)
            j.tools.sandboxer.libs_sandbox("%s/lib" % self.PACKAGEDIR, "%s/lib"% self.PACKAGEDIR, True)

        remove = ["codecs_jp", "codecs_hk", "codecs_cn", "codecs_kr", "testcapi", "tkinter", "audio"]
        # remove some stuff we don't need
        for item in j.sal.fs.listFilesInDir("%s/lib" % dest, recursive=True):
            if item.endswith(".c") or item.endswith(".h") or item.endswith(".pyc"):
                j.sal.fs.remove(item)
                pass
            for x in remove:
                if item.find(x) is not -1:
                    j.sal.fs.remove(item)
                    pass
        src="%s/github/threefoldtech/jumpscale_core/install/install.py"%j.dirs.CODEDIR

        j.sal.fs.copyFile(src,"%s/jumpscale_install.py"%dest)

        self._zip(dest=dest)


        def copy2git():

            #copy to sandbox & upload
            ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test",".git"]
            ignorefiles = ['.egg-info', ".pyc"]

            if j.core.platformtype.myplatform.isMac:
                url = "git@github.com:threefoldtech/sandbox_osx.git"
            elif j.core.platformtype.myplatform.isUbuntu:
                #TODO: need to check is ubuntu 1804, should only build there today
                url = "git@github.com:threefoldtech/sandbox_ubuntu.git"
            else:
                raise RuntimeError("only support OSX & Ubuntu")

            path = j.clients.git.getContentPathFromURLorPath(url)
            dest0 = "%s/base"%path
            src0 = dest
            j.sal.fs.createDir(dest0)
            j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=False, overwriteFiles=True,
                             ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True)



        copy2git()

        #now lets test if it all works
        j.sal.process.execute("set -e;cd %s;source env.sh;python3 jumpscale_install.py" % dest)
        j.sal.process.execute("set -e;cd %s;source env.sh;js_init generate" % dest)


        print("to test do:")
        print("'cd %s;source env.sh;js_shell" % dest)

    def _zip(self, dest="", python_lib_zip=False):
        if dest == "":
            dest = j.dirs.BUILDDIR + "/sandbox/python3/"
        cmd = "cd %s;rm -f ../js_sandbox.tar.gz;tar -czf ../js_sandbox.tar.gz .;" % dest
        j.sal.process.execute(cmd)
        if python_lib_zip:
            cmd = "cd %s;rm -f ../tfbot/lib/python.zip;cd ../tfbot/lib/python;zip -r ../python.zip .;" % dest
            j.sal.process.execute(cmd)
            cmd = "cd %s;rm -rf ../tfbot/lib/python" % dest
            j.sal.process.execute(cmd)


    def env_write(self, dest=""):
        """
        js_shell 'j.tools.sandboxer.python.env_write()'
        """

        if dest == "":
            dest = self.PACKAGEDIR

        C = """
        export PBASE=/sandbox

        export PATH=$PBASE/bin:/bin:/usr/local/bin:/usr/bin:/bin:$PATH
        export PYTHONPATH=$PBASE/lib/python:$PBASE/lib/pythonbin:$PBASE/lib/python.zip:$PBASE/lib/jumpscale:$PBASE/lib/pythonbin/lib-dynload:$PBASE/bin
        export PYTHONHOME=$PBASE

        export LIBRARY_PATH="$PBASE/bin:$PBASE/lib"
        export LD_LIBRARY_PATH="$LIBRARY_PATH"

        export LDFLAGS="-L$LIBRARY_PATH/"

        export LC_ALL=C.UTF-8
        export LANG=C.UTF-8

        export HOME=$PBASE/root
        export HOMEDIR=/root

        export PS1="3BOT: "
        
        cd $PBASE

        """
        j.sal.fs.writeFile("%s/env.sh" % dest, j.core.text.strip(C))
        # make sure to make the env.sh file executable
        j.sal.process.execute('chmod +x %s/env.sh' % dest)


        print("to test:\ncd %s;source env.sh" % dest)

    # def upload(self):
    #     """
    #     """
    #     if self.core.isMac:
    #         cmd = "cd %s/sandbox;scp -P 1022 js_sandbox.zip root@download.gig.tech:data/js_sandbox_osx.zip" % j.dirs.BUILDDIR
    #     else:
    #         cmd = "cd %s/sandbox;scp -P 1022 js_sandbox.zip root@download.gig.tech:data/js_sandbox_linux64.zip" % j.dirs.BUILDDIR
