from Jumpscale import j

import re
import os
from .SandboxPython import SandboxPython
from .Dep import Dep

JSBASE = j.application.JSBaseClass


class Sandboxer(JSBASE):
    """
    sandbox any linux app
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.sandboxer"
        JSBASE.__init__(self)

        self.original_size = 0
        self.new_size = 0
        self.python = SandboxPython()
        self.logger_enable()

    def _ldd(self, path, result=dict(), done=list()):
        self.logger.debug("find deb:%s" % path)
        if j.sal.fs.getFileExtension(path) in ["py", "pyc", "cfg", "bak", "txt",
                                               "png", "gif", "css", "js", "wiki", "spec", "sh", "jar", "xml", "lua"]:
            return result

        exclude = ["libpthread.so", "libltdl.so", "libm.so", "libresolv.so",
                   "libz.so", "libgcc", "librt", "libstdc++", "libapt", "libdbus", "libselinux"]

        if path not in done:
            cmd = "ldd %s" % path
            rc, out, _ = j.sal.process.execute(cmd, die=False)
            if rc > 0:
                if out.find("not a dynamic executable") != -1:
                    return result
            for line in out.split("\n"):
                line = line.strip()
                if line == "":
                    continue
                if line.find('=>') == -1:
                    continue

                name, lpath = line.split("=>")
                name = name.strip().strip("\t")
                name = name.replace("\\t", "")
                lpath = lpath.split("(")[0]
                lpath = lpath.strip()
                if lpath == "":
                    continue
                if name.find("libc.so") != 0 and name.lower().find("libx") != 0 and name not in done \
                        and name.find("libdl.so") != 0:
                    excl = False
                    for toexeclude in exclude:
                        if name.lower().find(toexeclude.lower()) != -1:
                            excl = True
                    if not excl:
                        self.logger.debug(("found:%s" % name))
                        try:
                            result[name] = Dep(name, lpath)
                            done.append(name)
                            result = self._ldd(lpath, result, done=done)
                        except Exception as e:
                            self.logger.debug(e)

        done.append(path)
        return result

    def _otool(self, path, result=dict(), done=list()):
        """
        like ldd on linux but for osx
        :param path:
        :param result:
        :param done:
        :return:
        """
        if j.sal.fs.getFileExtension(path) in ["py", "pyc", "cfg", "bak", "txt",
                                               "png", "gif", "css", "js", "wiki", "spec", "sh", "jar", "xml", "lua"]:
            return result

        exclude=["/usr/lib/libSystem","/System/Library/Frameworks/Core"]
        import pudb; pudb.set_trace()
        if path not in done:
            self.logger.debug(("check:%s" % path))
            name = j.sal.fs.getBaseName(path)
            cmd = "otool -L %s" % path
            rc, out, err = j.sal.process.execute(cmd, die=False)
            if rc > 0:
                raise RuntimeError(err)
                # if out.find("not a dynamic executable") != -1:
                #     return result
            for line in out.split("\n"):
                if len(line)>0 and line[0]==" ":
                    continue
                line = line.strip()
                if line == "":
                    continue
                lpath = line.split("(",1)[0].strip()
                if lpath == "":
                    continue
                excl = False
                for toexeclude in exclude:
                    if name.lower().find(toexeclude.lower()) != -1:
                        excl = True
                if not excl:
                    self.logger.debug(("found:%s" % name))
                    try:
                        result[name] = Dep(name, lpath)
                        done.append(name)
                        result = self._otool(lpath, result, done=done)
                    except Exception as e:
                        self.logger.debug(e)

        done.append(path)
        return result

    def _libs_find(self, path):
        """
        not needed to use manually, is basically ldd
        """
        self.logger.info("find deb:%s" % path)
        if j.core.platformtype.myplatform.isMac:
            result = self._otool(path, result=dict(), done=list())
            from IPython import embed; embed()
        else:
            result = self._ldd(path, result=dict(), done=list())
        return result

    def libs_sandbox(self, path, dest=None, recursive=False):
        """
        find binaries on path and look for supporting libs, copy the libs to dest
        default dest = '%s/bin/'%j.dirs.JSBASEDIR
        """
        self.logger.info("lib sandbox:%s" % path)
        if dest is None:
            dest = "%s/bin/" % j.dirs.BASEDIR
        j.sal.fs.createDir(dest)

        if j.sal.fs.isDir(path):
            # do all files in dir
            for item in j.sal.fs.listFilesInDir(path, recursive=False, followSymlinks=True, listSymlinks=False):
                if (j.sal.fs.isFile(item) and j.sal.fs.isExecutable(item)) or j.sal.fs.getFileExtension(item) == "so":
                    self.libs_sandbox(item, dest, recursive=False)
            if recursive:
                for item in j.sal.fs.listFilesAndDirsInDir(path, recursive=False):
                    self.libs_sandbox(item, dest, recursive)

        else:
            if (j.sal.fs.isFile(path) and j.sal.fs.isExecutable(path)) or j.sal.fs.getFileExtension(path) == "so":
                result = self._libs_find(path)
                for _,deb in list(result.items()):
                    deb.copyTo(dest)

    def copyTo(self, path, dest, excludeFileRegex=[], excludeDirRegex=[], excludeFiltersExt=["pyc", "bak"]):

        self.logger.info("SANDBOX COPY: %s to %s" % (path, dest))

        excludeFileRegex = [re.compile(r'%s' % item)
                            for item in excludeFileRegex]
        excludeDirRegex = [re.compile(r'%s' % item)
                           for item in excludeDirRegex]
        for extregex in excludeFiltersExt:
            excludeFileRegex.append(re.compile(r'(\.%s)$' % extregex))

        def callbackForMatchDir(path, arg):
            # self.logger.debug ("P:%s"%path)
            for item in excludeDirRegex:
                if(len(re.findall(item, path)) > 0):
                    return False
            return True

        def callbackForMatchFile(path, arg):
            # self.logger.debug ("F:%s"%path)
            for item in excludeFileRegex:
                if(len(re.findall(item, path)) > 0):
                    return False
            return True

        def callbackFile(src, args):
            path, dest = args
            subpath = j.sal.fs.pathRemoveDirPart(src, path)
            if subpath.startswith("dist-packages"):
                subpath = subpath.replace("dist-packages/", "")
            if subpath.startswith("site-packages"):
                subpath = subpath.replace("site-packages/", "")

            dest2 = dest + "/" + subpath
            j.sal.fs.createDir(j.sal.fs.getDirName(dest2))
            # self.logger.debug ("C:%s"%dest2)
            j.sal.fs.copyFile(src, dest2, overwriteFile=True)

        j.sal.fswalker.walkFunctional(path, callbackFunctionFile=callbackFile, callbackFunctionDir=None, arg=(
            path, dest), callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)

    # def _copy_chroot(self, path, dest):
    #     cmd = 'cp --parents -v "{}" "{}"'.format(path, dest)
    #     _, out, _ = j.sal.process.execute(cmd, die=False)
    #     return out

    # def sandbox_chroot(self, path, dest=None):
    #     """
    #     js_shell 'j.tools.sandboxer.sandbox_chroot()'
    #     """
    #     if dest is None:
    #         dest = "%s/bin/" % j.dirs.BASEDIR
    #     j.sal.fs.createDir(dest)
    #
    #     if not j.sal.fs.exists(path):
    #         raise RuntimeError('bin path "{}" not found'.format(path))
    #     self._copy_chroot(path, dest)
    #
    #     cmd = 'ldd "{}"'.format(path)
    #     _, out, _ = j.sal.process.execute(cmd, die=False)
    #     if "not a dynamic executable" in out:
    #         return
    #     for line in out.splitlines():
    #         dep = line.strip()
    #         if ' => ' in dep:
    #             dep = dep.split(" => ")[1].strip()
    #         if dep.startswith('('):
    #             continue
    #         dep = dep.split('(')[0].strip()
    #         self._copy_chroot(dep, dest)
    #
    #     if not j.sal.fs.exists(j.sal.fs.joinPaths(dest, 'lib64')):
    #         j.sal.fs.createDir(j.sal.fs.joinPaths(dest, 'lib64'))

    # def dedupe(self, path, storpath, name, excludeFiltersExt=[
    #            "pyc", "bak"], append=False, reset=False, removePrefix="", compress=True, delete=False, excludeDirs=[]):
    #     def copy2dest(src, removePrefix):
    #         if j.sal.fs.isLink(src):
    #             srcReal = j.sal.fs.readLink(src)
    #             if not j.sal.fs.isAbsolute(srcReal):
    #                 srcReal = j.sal.fs.joinPaths(j.sal.fs.getParent(src), srcReal)
    #         else:
    #             srcReal = src

    #         md5 = j.data.hash.md5(srcReal)
    #         dest2 = "%s/%s/%s/%s" % (storpath2, md5[0], md5[1], md5)
    #         dest2_bro = "%s/%s/%s/%s.bro" % (storpath2, md5[0], md5[1], md5)
    #         path_src = j.tools.path.get(srcReal)
    #         self.original_size += path_src.size
    #         if compress:
    #             self.logger.debug("- %-100s %sMB" % (srcReal, round(path_src.size / 1000000, 1)))
    #             if delete or not j.sal.fs.exists(dest2_bro):
    #                 cmd = "bro --quality 7 --input '%s' --output %s" % (srcReal, dest2_bro)
    #                 # self.logger.debug (cmd)
    #                 j.sal.process.execute(cmd)
    #                 if not j.sal.fs.exists(dest2_bro):
    #                     raise j.exceptions.RuntimeError("Could not do:%s" % cmd)
    #                 path_dest = j.tools.path.get(dest2_bro)
    #                 size = path_dest.size
    #                 self.new_size += size
    #                 if not self.original_size == 0:
    #                     efficiency = round(self.new_size / self.original_size, 3)
    #                 else:
    #                     efficiency = 1
    #                 if not path_src.size == 0:
    #                     efficiency_now = round(path_dest.size / path_src.size, 3)
    #                 else:
    #                     efficiency_now = 0
    #                 self.logger.debug("- %-100s %-6s %-6s %sMB" %
    #                       ("", efficiency, efficiency_now, round(self.original_size / 1000000, 1)))
    #         else:
    #             j.sal.fs.copyFile(srcReal, dest2)

    #         stat = j.sal.fs.statPath(srcReal)

    #         if removePrefix != "":
    #             if src.startswith(removePrefix):
    #                 src = src[len(removePrefix):]
    #                 if src[0] != "/":
    #                     src = "/" + src

    #         out = "%s|%s|%s\n" % (src, md5, stat.st_size)
    #         return out

    #     if reset:
    #         j.sal.fs.removeDirTree(storpath)

    #     storpath2 = j.sal.fs.joinPaths(storpath, "files")
    #     j.sal.fs.createDir(storpath2)
    #     j.sal.fs.createDir(j.sal.fs.joinPaths(storpath, "md"))
    #     for i1 in "1234567890abcdef":
    #         for i2 in "1234567890abcdef":
    #             j.sal.fs.createDir("%s/%s/%s" % (storpath2, i1, i2))

    #     self.logger.debug("DEDUPE: %s to %s" % (path, storpath))

    #     plistfile = j.sal.fs.joinPaths(storpath, "md", "%s.flist" % name)

    #     if append and j.sal.fs.exists(path=plistfile):
    #         out = j.sal.fs.fileGetContents(plistfile)
    #     else:
    #         j.sal.fs.remove(plistfile)
    #         out = ""

    #     # excludeFileRegex=[]
    #     # for extregex in excludeFiltersExt:
    #     #     excludeFileRegex.append(re.compile(ur'(\.%s)$'%extregex))
    #     def skipDir(src):
    #         for d in excludeDirs:
    #             if src.startswith(d):
    #                 return True
    #         return False

    #     if not j.sal.fs.isDir(path):
    #         out += copy2dest(path, removePrefix)
    #     else:
    #         for src in j.sal.fs.listFilesInDir(path, recursive=True, exclude=[
    #                                            "*.pyc", "*.git*"], followSymlinks=True, listSymlinks=True):
    #             if skipDir(src):
    #                 continue
    #             out += copy2dest(src, removePrefix)

    #     out = j.core.text.sort(out)
    #     j.sal.fs.writeFile(plistfile, out)

    # def sandboxBinWithPrefab(self, prefab, bin_path, sandbox_dir):
    #     """
    #     Sandbox a binary located in `bin_path` into a sandbox / filesystem

    #     @param prefab Prefab: prefab either local or remote on a machine.
    #     @param bin_path string: binary full path to sandbox.
    #     @param sandbox_dir string: where to create the sandbox.

    #     """

    #     prefab.core.dir_remove(sandbox_dir)
    #     prefab.core.dir_ensure(sandbox_dir)

    #     LIBSDIR = j.sal.fs.joinPaths(sandbox_dir, 'lib')
    #     BINDIR = j.sal.fs.joinPaths(sandbox_dir, 'bin')
    #     prefab.core.dir_ensure(LIBSDIR)
    #     prefab.core.dir_ensure(BINDIR)
    #     prefab.core.dir_ensure(j.sal.fs.joinPaths(sandbox_dir, 'usr'))

    #     for directory in ['opt', 'var', 'tmp', 'root']:
    #         prefab.core.dir_ensure(j.sal.fs.joinPaths(sandbox_dir, directory))

    #     # copy needed binaries and required libs
    #     prefab.core.execute_bash("""js_shell 'j.tools.sandboxer.libs_sandbox("{}", dest="{}")'""".format(bin_path, LIBSDIR))

    #     prefab.core.file_copy(bin_path, BINDIR+'/')

    # def sandboxBinLocal(self, bin_path, sandbox_dir):
    #     """
    #     Sandbox a binary located in `bin_path` into a sandbox / filesystem

    #     @param bin_path string: binary full path to sandbox.
    #     @param sandbox_dir string: where to create the sandbox.

    #     """
    #     try:
    #         j.sal.fs.removeDir(sandbox_dir)
    #     except Exception as e:
    #         pass

    #     j.sal.fs.createDir(sandbox_dir)

    #     LIBSDIR = j.sal.fs.joinPaths(sandbox_dir, 'lib')
    #     BINDIR = j.sal.fs.joinPaths(sandbox_dir, 'bin')
    #     j.sal.fs.createDir(LIBSDIR)
    #     j.sal.fs.createDir(BINDIR)
    #     j.sal.fs.createDir(j.sal.fs.joinPaths(sandbox_dir, 'usr'))

    #     for directory in ['opt', 'var', 'tmp', 'root']:
    #         j.sal.fs.createDir(j.sal.fs.joinPaths(sandbox_dir, directory))

    #     # copy needed binaries and required libs
    #     j.tools.sandboxer.libs_sandbox(bin_path, dest=LIBSDIR)
    #     j.sal.fs.copyFile(bin_path, BINDIR+'/')

