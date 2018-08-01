from jumpscale import j
from .DocSite import DocSite


import imp
import time
import sys

JSBASE = j.application.jsbase_get_class()


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod

class MarkDownDocs(JSBASE):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.markdowndocs"
        JSBASE.__init__(self)
        self.__imports__ = "toml"
        self._macroPathsDone = []
        self._initOK = False
        self._macroCodepath = j.sal.fs.joinPaths(
            j.dirs.VARDIR, "markdowndocs_internal", "macros.py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(
            j.dirs.VARDIR, "markdowndocs_internal"))

        self.docsites = {}  # location in the outpath per site
        self.outpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "markdowndocs")
        self._git_repos = {}
        self.defs = {}

        self._loaded = []  # don't double load a dir
        self._configs = []  # all found config files
        self._macros_loaded = []

        self._pointer_cache = {}  # so we don't have to full lookup all the time

        self.logger_enable()

    def _git_get(self, path):
        if path not in self._git_repos:
            try:
                gc = j.clients.git.get(path)
            except Exception as e:
                print("cannot load git:%s"%path)
                return
            self._git_repos[path] = gc
        return self._git_repos[path]

    def _init(self):
        if not self._initOK:
            # self.install()
            j.clients.redis.core_get()
            j.sal.fs.remove(self._macroCodepath)
            # load the default macro's
            self.macros_load("https://github.com/Jumpscale/markdowndocs/tree/master/macros")
            self._initOK = True

    def macros_load(self, pathOrUrl=""):
        """
        @param pathOrUrl can be existing path or url
        e.g. https://github.com/threefoldtech/jumpscale_lib/markdowndocs/tree/master/examples
        """
        self.logger.info("load macros")
        path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

        if path not in self._macroPathsDone:

            if not j.sal.fs.exists(path=path):
                raise j.exceptions.Input(
                    "Cannot find path:'%s' for macro's, does it exist?" % path)

            if j.sal.fs.exists(path=self._macroCodepath):
                code = j.sal.fs.readFile(self._macroCodepath)
            else:
                code = ""

            for path0 in j.sal.fs.listFilesInDir(path, recursive=True, filter="*.py", followSymlinks=True):
                newdata = j.sal.fs.fileGetContents(path0)
                md5 = j.data.hash.md5_string(newdata)
                if md5 not in self._macros_loaded:
                    code += newdata
                    self._macros_loaded.append(md5)

            code = code.replace("from jumpscale import j", "")
            code = "from jumpscale import j\n\n" + code

            j.sal.fs.writeFile(self._macroCodepath, code)
            self.macros = loadmodule("macros", self._macroCodepath)
            self._macroPathsDone.append(path)

    def load(self, path="", name=""):
        if path.startswith("http"):
            path = j.clients.git.getContentPathFromURLorPath(path)
        ds = DocSite(path=path, name=name)
        self.docsites[ds.name] = ds
        
    def git_update(self):
        if self.docsites == {}:
            self.load()
        for gc in self._git_repos:
            gc.pull()

    def item_get(self, name, namespace="", die=True, first=False):
        """
        """
        key = "%s_%s" % (namespace, name)

        import pudb; pudb.set_trace()       

        # we need the cache for performance reasons
        if not key in self._pointer_cache:

            # make sure we have the most dense ascii name for search
            ext = j.sal.fs.getFileExtension(name).lower()
            name = name[:-(len(ext)+1)]  # name without extension
            name = j.data.text.strip_to_ascii_dense(name)

            namespace = j.data.text.strip_to_ascii_dense(namespace)

            if not namespace == "":
                ds = self.docsite_get(namespace)
                res = self._items_get(name, ds=ds)

                # found so will return & remember
                if len(res) == 1:
                    self._pointer_cache[key] = res[0]
                    return res

                # did not find so namespace does not count

            res = self._items_get(name=name, ext=ext)

            if (first and len(res)==0) or not len(res) == 1:
                if die:
                    raise j.exceptions.Input(
                        message="Cannot find item with name:%s in namespace:'%s'" % (name, namespace))
                else:
                    self._pointer_cache[key] = None
            else:
                self._pointer_cache[key] = res[0]

        return self._pointer_cache[key]

    def _items_get(self, name, ext, ds=None, res=[]):
        """
        @param ds = DocSite, optional, if specified then will only look there
        """

        if ds is not None:

            if ext in ["md"]:
                find_method = ds.doc_get
            if ext in ["html", "htm"]:
                find_method = ds.html_get
            else:
                find_method = ds.file_get

            res0 = find_method(name=name+"."+ext, die=False)

            if res0 is not None:
                # we have a match, lets add to results
                res.append(res0)

        else:
            for key, ds in self.docsites.items():
                res = self._items_get(name=name, ext=ext, ds=ds, res=res)

        return res

    def def_get(self, name):
        name = j.data.text.strip_to_ascii_dense(name)
        if name not in self.defs:
            raise RuntimeError("cannot find def:%s" % name)
        return self.defs[name]

    def docsite_get(self, name, die=True):
        name = j.data.text.strip_to_ascii_dense(name)
        name = name.lower()
        if name in self.docsites:
            return self.docsites[name]
        if die:
            raise j.exceptions.Input(message="Cannot find docsite with name:%s" %
                                     name, level=1, source="", tags="", msgpub="")
        else:
            return None

       

    # def scan_load(self, pathOrUrl="", name=""):
    #     """

    #     js_shell 'j.tools.markdowndocs.load()'

    #     will look for config.toml in $source/config.toml

    #     @param pathOrUrl is the location where the markdown or html docs are which need to be processed
    #         if not specified then will look for root of git repo and add docs
    #         source = $gitrepoRootDir/docs

    #         this can also be a git url e.g. https://github.com/Jumpscale/markdowndocs/tree/master/examples

    #     """
    #     if pathOrUrl == "":
    #         pathOrUrl = j.sal.fs.getcwd()
    #     if pathOrUrl in self._loaded:
    #         return
    #     self.logger.info("load:%s" % pathOrUrl)
    #     self._loaded.append(pathOrUrl)
    #     self._init()
    #     if pathOrUrl == "":
    #         path = j.sal.fs.getcwd()
    #     else:
    #         path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

    #     for configPath in j.sal.fs.listFilesInDir(path, recursive=True, filter="docs_config.toml"):
    #         if configPath not in self._configs:
    #             self.logger.debug("found configPath for doc dir:%s" % configPath)
    #             ds = DocSite(self, configPath=configPath, name=name)
    #             self.docsites[ds.name] = ds
