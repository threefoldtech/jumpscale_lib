from js9 import j
from .Doc import Doc
from .DocBase import DocBase
from .HtmlPage import HtmlPage

import copy

import imp
import sys

def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod

JSBASE = j.application.jsbase_get_class()


class DocSite(JSBASE):
    """
    """

    def __init__(self, docgen, configPath,name=""):
        JSBASE.__init__(self)

        self.docgen = docgen

        #init initial arguments
        self.path = j.sal.fs.getDirName(configPath)
        # self.theme = theme
        # self.template = template

        self.config = j.data.serializer.toml.load(configPath)

        if not name:
            if "name" not in self.config:                        
                self.name = j.sal.fs.getBaseName(self.path.rstrip("/")).lower()
            else:
                self.name = self.config["name"].lower()
        else:
            self.name = name.lower()

        self.name = j.data.text.strip_to_ascii_dense(self.name)

        # if "docsify" in template:
        #     self.hugo = False
        # else:
        #     self.hugo = True

        gitpath = j.clients.git.findGitPath(self.path)
        if gitpath not in self.docgen._git_repos:
            self.git = j.tools.docgenerator._git_get(gitpath)
            self.docgen._git_repos[gitpath] = self.git

        self.defs = {}
        self.content_default = {}  # key is relative path in docsite where default content found

        # # in caddy config specify the baseurl
        # ws = "%s%s/" % (j.tools.docgenerator.webserver, self.name)
        # self.config["baseurl"] = ws

        # need to empty again, because was used in config
        self.data_default = {}  # key is relative path in docsite where default content found

        self.docs = {}
        self.htmlpages = {}
        self.others = {}
        self.files = {}

        # self.template_path = j.clients.git.getContentPathFromURLorPath(self.template)
        # self.generator_path = j.sal.fs.joinPaths(self.template_path, "generator.py")

        # self.doc_add_meta = False

        # check if there are dependencies
        if 'docs' in self.config:
            for item in self.config['docs']:
                if "name" not in item or "url" not in item:
                    raise RuntimeError("config docs item:%s not well defined in %s"%(item,self))
                name = item["name"].strip().lower()
                url = item["url"].strip()
                path = j.clients.git.getContentPathFromURLorPath(url)
                j.tools.docgenerator.load(path,name=name)

        # if 'doc_add_meta' in self.config:
        #     self.doc_add_meta = bool(self.config['doc_add_meta'])

        # # lets make sure its the outpath at this time and not the potentially changing one
        # self.outpath = j.sal.fs.joinPaths(copy.copy(j.tools.docgenerator.outpath), self.name)

        # self._generator = None

        self.logger_enable()
        self.logger.level=1

        self.load()
        

    # @property
    # def config_template(self):
        
    #     from jinja2 import Environment, FileSystemLoader, select_autoescape
    #     j2_env = Environment(
    #         loader = FileSystemLoader(self.template_path),
    #         autoescape=select_autoescape(['html', 'xml'])
    #     )
    #     config_template = j2_env.get_template('config.toml')  
    #     return config_template

    # @property
    # def config(self):
    #     if not self._config:
    #         cfgpath = self.path + "config.toml"
    #         if  j.sal.fs.exists(cfgpath, followlinks=True):
    #             c = j.sal.fs.fileGetContents(cfgpath)
    #             self._config = j.data.serializer.toml.loads(c)
    #             self.name = self._config["name"].strip().lower()
    #             if "template" in self._config:
    #                 self.template = self._config["template"].strip()
    #             else:
    #                 self.template = ""
    #             if "theme" in self._config:
    #                 self.theme = self._config["theme"].strip()
    #             else:
    #                 self.theme = ""
    #     return self._config

    def _processData(self, path):
        ext = j.sal.fs.getFileExtension(path).lower()
        if ext == "":
            # try yaml & toml
            self._processData(path + ".toml")
            self._processData(path + ".yaml")
            return

        if not j.sal.fs.exists(path):
            return {}

        if ext == "toml":
            data = j.data.serializer.toml.load(path)
        elif ext == "yaml":
            data = j.data.serializer.yaml.load(path)
        else:
            raise j.exceptions.Input(message="only toml & yaml supported", level=1, source="", tags="", msgpub="")

        if not j.data.types.dict.check(data):
            raise j.exceptions.Input(message="cannot process toml/yaml on path:%s, needs to be dict." %
                                     path, level=1, source="", tags="", msgpub="")

            # dont know why we do this? something todo probably with mustache and dots?
        keys = [str(key) for key in data.keys()]
        for key in keys:
            if key.find(".") != -1:
                data[key.replace(".", "_")] = data[key]
                data.pop(key)

        fulldirpath = j.sal.fs.getDirName(path)
        rdirpath = j.sal.fs.pathRemoveDirPart(fulldirpath, self.path)
        rdirpath = rdirpath.strip("/").strip().strip("/")
        import pudb; pudb.set_trace()
        self.data_default[rdirpath] = data

    # @property
    # def url(self):
    #     return "%s/%s" % (j.tools.docgenerator.webserver, self.name)

    # @property
    # def sitepath(self):
    #     return "/%s/" % (self.name)

    def load(self):
        """
        walk in right order over all files which we want to potentially use (include)
        and remember their paths

        if duplicate only the first found will be used

        """
        j.sal.fs.remove(self.path + "errors.md")
        path = self.path
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.NotFound("Cannot find source path in load:'%s'" % path)


        def clean(name):
            return j.data.text.strip_to_ascii_dense(name)

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path)
            if base.startswith("."):
                return False

            # if base.startswith("_"):
            #     return False

            # check if we find a macro dir, if so load
            if base == "macros":
                j.tools.docgenerator.macros_load(path=path)

            # if base in ["static"]:
            #     return False

            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            # if base.startswith("_"):
            #     return False
            ext = j.sal.fs.getFileExtension(path)
            # if not ext in ["md", "yaml", "toml"]:
            #     return False
            if ext == "md" and base[:-3] in ["summary", "default"]:
                return False

            if base.startswith("_"):
                return False

            # if base[:-3].lower() in ["readme"]:
            #     return False

            return True

        def callbackFunctionDir(path, arg):
            # will see if ther eis data.toml or data.yaml & load in data structure in this obj
            self._processData(path + "/data")
            dpath = path + "/default.md"
            if j.sal.fs.exists(dpath, followlinks=True):
                C = j.sal.fs.fileGetContents(dpath)
                rdirpath = j.sal.fs.pathRemoveDirPart(path, self.path)
                rdirpath = rdirpath.strip("/").strip().strip("/")
                self.content_default[rdirpath] = C
            return True

        def callbackFunctionFile(path, arg):
            self.logger.debug("file:%s"%path)
            ext = j.sal.fs.getFileExtension(path).lower()
            base = j.sal.fs.getBaseName(path)
            if ext == "md":
                self.logger.debug("found md:%s"%path)
                base = base[:-3]  # remove extension
                doc = Doc(path, base, docsite=self)
                if base not in self.docs:
                    self.docs[base.lower()] = doc
                self.docs[doc.name_dot_lower] = doc
            elif ext in ["html","htm"]:
                self.logger.debug("found html:%s"%path)
                l = len(ext)+1
                base = base[:-l]  # remove extension
                doc = HtmlPage(path, base, docsite=self)
                if base not in self.htmlpages:
                    self.htmlpages[base.lower()] = doc
                self.htmlpages[doc.name_dot_lower] = doc
            else:
                
                if ext in ["png", "jpg", "jpeg", "pdf", "docx", "doc", "xlsx", "xls", \
                            "ppt", "pptx", "mp4","css","js"]:
                    self.logger.debug("found file:%s"%path)
                    if base in self.files:
                        raise j.exceptions.Input(message="duplication file in %s,%s" %
                                                 (self, path), level=1, source="", tags="", msgpub="")
                    self.files[base.lower()] = path
                # else:
                #     self.logger.debug("found other:%s"%path)
                #     l = len(ext)+1
                #     base = base[:-l]  # remove extension
                #     doc = DocBase(path, base, docsite=self)
                #     if base not in self.others:
                #         self.others[base.lower()] = doc
                #     self.others[doc.name_dot_lower] = doc
                    

        callbackFunctionDir(self.path, "")  # to make sure we use first data.yaml in root

        j.sal.fswalker.walkFunctional(
            self.path,
            callbackFunctionFile=callbackFunctionFile,
            callbackFunctionDir=callbackFunctionDir,
            arg="",
            callbackForMatchDir=callbackForMatchDir,
            callbackForMatchFile=callbackForMatchFile)

    # def file_add(self, path):
    #     if not j.sal.fs.exists(path, followlinks=True):
    #         raise j.exceptions.Input(message="Cannot find path:%s" % path, level=1, source="", tags="", msgpub="")
    #     base = j.sal.fs.getBaseName(path).lower()
    #     self.files[base] = path

    # def files_copy(self, destination=None):
    #     if not destination:
    #         if self.hugo:
    #             destination = "static/files"
    #         else:
    #             destination = "files"
    #     dpath = j.sal.fs.joinPaths(self.outpath, destination)
    #     j.sal.fs.createDir(dpath)
    #     for name, path in self.files.items():
    #         j.sal.fs.copyFile(path, j.sal.fs.joinPaths(dpath, name))

    def process(self):
        for key, doc in self.docs.items():
            doc.process()

    # @property
    # def generator(self):
    #     """
    #     is the generation code which is in directory of the template, is called generate.py and is in root of template dir
    #     """
    #     if self._generator is None:
    #         self._generator = loadmodule(self.name, self.generator_path)
    #     return self._generator

    def error_raise(self, errormsg, doc=None):
        if doc is not None:
            errormsg2 = "## ERROR: %s\n\n- in doc: %s\n\n%s\n" % (j.data.time.getLocalTimeHR(), doc, errormsg)
            j.sal.fs.writeFile(filename=self.path + "errors.md", contents=errormsg2, append=True)
            self.logger.error(errormsg2)
            doc.errors.append(errormsg)
        else:
            from IPython import embed
            self.logger.error("DEBUG NOW raise error")
            embed()
            raise RuntimeError("stop debug here")

    # def write(self):
    #     if self._config:
    #         j.sal.fs.removeDirTree(self.outpath)
    #         dest = j.sal.fs.joinPaths(self.outpath, "content")
    #         j.sal.fs.createDir(dest)
    #         # source = self.path
    #         # j.do.copyTree(source, dest, overwriteFiles=True, ignoredir=['.*'], ignorefiles=[
    #         #               "*.md", "*.toml", "_*", "*.yaml", ".*"], rsync=True, recursive=True, rsyncdelete=False)

    #         for key, doc in self.docs.items():
    #             doc.process()

    #         # find the defs, also process the aliases
    #         for key, doc in self.docs.items():
    #             if "tags" in doc.data:
    #                 tags = doc.data["tags"]
    #                 if "def" in tags:
    #                     name = doc.name.lower().replace("_", "").replace("-", "").replace(" ", "")
    #                     self.defs[name] = doc
    #                     if "alias" in doc.data:
    #                         for alias in doc.data["alias"]:
    #                             name = alias.lower().replace("_", "").replace("-", "").replace(" ", "")
    #                             self.defs[name] = doc

    #         for key, doc in self.docs.items():
    #             # doc.defs_process()
    #             doc.write()

    #         self.generator.generate(self)

    #         if j.sal.fs.exists(j.sal.fs.joinPaths(self.path, "static"), followlinks=True):
    #             j.sal.fs.copyDirTree(j.sal.fs.joinPaths(self.path, "static"), j.sal.fs.joinPaths(self.outpath, "public"))
    #     else:
    #         self.logger.info("no need to write:%s"%self.path)

    def file_get(self, name, die=True):
        for key, val in self.files.items():
            if key.lower() == name.lower():
                return key
            # ext = j.sal.fs.getFileExtension(key)
            # nameLower = key[:-(len(ext) + 1)]
            # if nameLower == name.lower():
            #     return key
        if die:
            raise j.exceptions.Input(message="Did not find file:%s in %s" %
                                     (name, self), level=1, source="", tags="", msgpub="")
        return None

    def doc_get(self, name, die=True):
        name = name.lower()
        if name in self.docs:
            return self.docs[name]
        if die:
            raise j.exceptions.Input(message="Cannot find doc with name:%s" % name, level=1, source="", tags="", msgpub="")
        else:
            return None

    def html_get(self, name, die=True):
        if "." in name:
            ext =  j.sal.fs.getFileExtension(name).lower()
            name = name[:-(len(ext)+1)] #name without extension
        name = j.data.text.strip_to_ascii_dense(name)
        if name in self.htmlpages:
            return self.htmlpages[name]
        if die:
            raise j.exceptions.Input(message="Cannot find doc with name:%s" % name, level=1, source="", tags="", msgpub="")
        else:
            return None            

    def __repr__(self):
        return "docsite:%s" % ( self.path)

    __str__ = __repr__