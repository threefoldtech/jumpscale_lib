from js9 import j
from .Doc import Doc
from .DocBase import DocBase
from .DocWatchdog import DocWatchdog
from .HtmlPage import HtmlPage
JSBASE = j.application.jsbase_get_class()

import copy

import imp
import sys

def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod



class DocSite(JSBASE):
    """
    """

    def __init__(self, path,name=""):
        JSBASE.__init__(self)

        self.docgen = j.tools.docgenerator

        #init initial arguments

        config_path = j.sal.fs.joinPaths(path,"docs_config.toml")
        config_path2 = j.sal.fs.joinPaths(path,"docs/docs_config.toml")
        if not j.sal.fs.exists(config_path) and j.sal.fs.exists(config_path2):
            config_path=config_path2
            path = j.sal.fs.joinPaths(path,"docs")
        if j.sal.fs.exists(config_path):
            self.config = j.data.serializer.toml.load(config_path)
        else:
            raise RuntimeError("cannot find docs_config in %s"%config_path)

        self.path = path
        if not j.sal.fs.exists(path):
            raise RuntimeError("Cannot find path:%s"%path)


        if not name:
            if "name" not in self.config:                        
                self.name = j.sal.fs.getBaseName(self.path.rstrip("/")).lower()
            else:
                self.name = self.config["name"].lower()
        else:
            self.name = name.lower()

        self.name = j.data.text.strip_to_ascii_dense(self.name)

        self.defs = {}
        self.content_default = {}  # key is relative path in docsite where default content found

        # need to empty again, because was used in config
        self.data_default = {}  # key is relative path in docsite where default content found

        self.docs = {}
        self.htmlpages = {}
        self.others = {}
        self.files = {}
        self.sidebars = {}
        self._processed = False

    
        # check if there are dependencies
        if 'docs' in self.config:
            for item in self.config['docs']:
                if "name" not in item or "url" not in item:
                    raise RuntimeError("config docs item:%s not well defined in %s"%(item,self))
                name = item["name"].strip().lower()
                url = item["url"].strip()
                path = j.clients.git.getContentPathFromURLorPath(url)
                j.tools.docgenerator.load(path,name=name)

        self.logger_enable()
        self.logger.level=1

        self._git=None
        self._watchdog=None

        self.logger.info("loaded:%s"%self)
        

    @property
    def git(self):
        if self._git is None:
            gitpath = j.clients.git.findGitPath(self.path,die=False)
            if not gitpath:
                return
            if gitpath not in self.docgen._git_repos:
                self._git = j.tools.docgenerator._git_get(gitpath)
                self.docgen._git_repos[gitpath] = self.git   
        return self._git      

    @property
    def urls(self):
        urls = [item for item in self.docs.keys()]
        urls.sort()
        return urls

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
            base = j.sal.fs.getBaseName(path).lower()
            if base.startswith("."):
                return False
            if base.startswith("_"):
                return False
            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            if base == "_sidebar.md":
                return True
            if base.startswith("_"):
                return False
            ext = j.sal.fs.getFileExtension(path)
            if ext == "md" and base[:-3] in ["summary", "default"]:
                return False
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
                # if base not in self.docs:
                #     self.docs[base.lower()] = doc
                self.docs[doc.name_dot_lower] = doc
            elif ext in ["html","htm"]:
                self.logger.debug("found html:%s"%path)
                l = len(ext)+1
                base = base[:-l]  # remove extension
                doc = HtmlPage(path, base, docsite=self)
                # if base not in self.htmlpages:
                #     self.htmlpages[base.lower()] = doc
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
        self._processed = True

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

    def load_process(self):
        self.load()
        self.process()

    def file_get(self, name, die=True):
        if not self._processed:
            self.load_process()
        
        for key, val in self.files.items():
            if key.lower() == name.lower():
                return val
        if die:
            raise j.exceptions.Input(message="Did not find file:%s in %s" %
                                     (name, self), level=1, source="", tags="", msgpub="")
        return None

    def doc_get(self, name, die=True):
        
        if not self._processed:
            self.load_process()

        if j.data.types.list.check(name):
            name = "/".join(name)

        name = name.strip("/")
        name = name.lower()            

        if name.endswith(".md"):
            name=name[:-3] #remove .md
            
        if "/" in name:
            name = name.replace("/",".")

        name = name.strip(".")  #lets make sure its clean again


        #let caching work
        if name in self.docs:
            if self.docs[name] is None and die:
                raise j.exceptions.Input(message="Cannot find doc with name:%s" % name, level=1, source="", tags="", msgpub="")    
            return self.docs[name]

        #build candidates to search
        candidates = [name]
        if name.endswith("readme"):
            candidates.append(name[:-6]+"index")
        else:
            candidates.append(name+".readme")

        if name.endswith("index"):            
            nr,res = self._doc_get(name[:-5]+"readme")
            if nr==1:
                return 1,res
            name = name[:-6]
        else:
            candidates.append(name+".index")

        #look for $fulldirname.$dirname as name of doc
        if "." in name: 
            name0 = name+"."+name.split(".")[-1]
            candidates.append(name0)

        for cand in candidates:
            nr,res = self._doc_get(cand)
            if nr == 1:
                self.docs[name] = res  #remember for caching
                return self.docs[name]

        if die:
            raise j.exceptions.Input(message="Cannot find doc with name:%s" % name, level=1, source="", tags="", msgpub="")
        else:
            return None

    def _doc_get(self, name):
                
        if name in self.docs:
            return 1, self.docs[name]
    
        res = []
        for key,item in self.docs.items():
            if name in  item.name_dot_lower:
                res.append(key)
        if len(res)>0:
            return  len(res),self.docs[res[0]]
        else:
            return 0,None


    def html_get(self, name, die=True):
        if not self._processed:
            self.load_process()        
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

    def sidebar_get(self, url):
        """
        will calculate the sidebar, if not in url will return None
        """
        if not self._processed:
            self.load_process()        
        if j.data.types.list.check(url):
            url = "/".join(url)
        self.logger.debug("sidebar_get:%s"%url)            
        if url in self.sidebars:
            return self.sidebars[url]

        url_original = copy.copy(url)
        url = url.strip("/")
        url = url.lower()

        if url.endswith(".md"):
            url = url[:-3]

        url = url.replace("/",".")
        url = url.strip(".")

        if url == "":
            self.sidebars[url_original]=None
            return None

        if "_sidebar" not in url:
            self.sidebars[url_original]=None
            return None #did not find sidebar just return None


        if url in self.docs:
            self.sidebars[url_original] = self._sidebar_process(self.docs[url].content,url_original=url_original)
            return self.sidebars[url_original]                        
            
        #did not find the usual location, lets see if we can find the doc allone
        url0=url.replace("_sidebar","").strip().strip(".").strip()
        if "." in url0: #means we can 
            name=url0.split(".")[-1]
            doc=self.doc_get(name,die=False)
            if doc:
                #we found the doc, so can return the right sidebar
                possiblepath = doc.path_dir_rel.replace("/",".").strip(".")+"._sidebar"
                if not possiblepath == url:
                    return self.get(possiblepath)

        #lets look at parent
        
        if url0=="":
            raise RuntimeError("cannot be empty")
            
        newurl = ".".join(url0.split(".")[:-1])+"._sidebar"
        return self.sidebar_get(newurl)
            
        self.sidebars[url_original] = self._sidebar_process(self.docs[url].content,url_original=url_original)
        return self.sidebars[url_original]

    def _sidebar_process(self,c,url_original):
        
        def clean(c):
            out= ""
            state = "start"
            for line in c.split("\n"):
                lines = line.strip()
                if lines.startswith("*"):
                    lines=lines[1:]
                if lines.startswith("-"):
                    lines=lines[1:]
                if lines.startswith("+"):
                    lines=lines[1:]
                lines = lines.strip()
                if lines == "":
                    continue
                if line.find("(/)") is not -1:
                    continue
                if line.find("---") is not -1:
                    if state == "start":
                        continue
                    state="next"
                out+=line+"\n"
            return out

        c=clean(c)

        out= "* [Home](/)\n"
        
        for line in c.split("\n"):
            if line.strip()=="":
                out+="\n\n"
                continue
            
            if "(" in line and ")" in line:
                url = line.split("(",1)[1].split(")")[0]
            else:
                url = ""
            if "[" in line and "]" in line:
                descr = line.split("[",1)[1].split("]")[0]
                pre = line.split("[")[0]
                pre = pre.replace("* ","").replace("- ","")
            else:
                descr = line
                pre = "<<"

            if url:
                doc = self.doc_get(url,die=False)
                if doc is None:
                    out+="%s* NOTFOUND:%s"%(pre,url)                    
                else:
                    out+="%s* [%s](/%s)\n"%(pre,descr,doc.name_dot_lower.replace(".","/"))

            else:                                    
                if not pre:
                    pre = "    "
                if pre is not  "<<":
                    out+="%s* %s\n"%(pre,descr)
                else:
                    out+="%s\n"%(descr)

        res = self.doc_get("_sidebar_parent",False)
        if res:
            out+=res.content            
        else:
            out+="----\n\n"
            for key,val in j.tools.docgenerator.docsites.items():
                if key.startswith("www"):
                    continue
                out+="[%s](../%s/)\n"%(key,key)

        return out

    def __repr__(self):
        return "docsite:%s" % ( self.path)

    __str__ = __repr__

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