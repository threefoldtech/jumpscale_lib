from js9 import j
import toml

import copy

JSBASE = j.application.jsbase_get_class()


class Doc(JSBASE):
    """
    """

    def __init__(self, path, name, docsite):
        JSBASE.__init__(self)
        self.path = path
        self.docsite = docsite

        self.cat = ""
        if "/blogs/" in path or "/blog/" in path:
            self.cat = "blog"
        if "/defs/" in path or "/def/" in path:
            self.cat = "def"            
        
        self.path_dir = j.sal.fs.getDirName(self.path)
        self.path_dir_rel = j.sal.fs.pathRemoveDirPart(self.path_dir, self.docsite.path).strip("/")
        self.name = j.data.text.strip_to_ascii_dense(name)
        self.name_original = name
        self.path_rel = j.sal.fs.pathRemoveDirPart(path, self.docsite.path).strip("/")

        name_dot =  "%s/%s" % (self.path_dir_rel,name)
        self.name_dot = name_dot.replace("/",".")
        self.name_dot_lower = self.name_dot.replace("/",".").lower().strip(".")

        # self.content = ""
        # self.show = True
        self.errors = []

        if j.sal.fs.getDirName(self.path).strip("/").split("/")[-1][0] == "_":
            # means the subdir starts with _
            self.show = False

        self._processed = False

        self._extension = None

        self._data = {} #is all data, from parents as well, also from default data

        self._md = None


    @property
    def extension(self):
        if not self._extension:
           self._extension = j.sal.fs.getFileExtension(self.path)        
        return self._extension

    @property
    def title(self):
        if "title" in self.data:
            return self.data["title"]
        else:
            self.error_raise("Could not find title in doc.")

    def error_raise(self, msg):
        return self.docsite.error_raise(msg, doc=self)            

    @property
    def data(self):
        if self._data=={}:
            self._data_default_process()    
            print("data update from md")
            from IPython import embed;embed(colors='Linux')
            s    
        return self._data

    @property
    def md(self):
        if not self._md :
            self._md = j.data.markdown.document_get(j.sal.fs.fileGetContents(self.path))        
        return self._md

    @property
    def content_(self):
        print('content')
        from IPython import embed;embed(colors='Linux')
        s

    @property
    def content_clean(self):
        # remove the code blocks (comments are already gone)
        print('content_clean')
        from IPython import embed;embed(colors='Linux')
        s

    @property
    def content_clean_summary(self):
        c = self.content_clean
        lines = c.split("\n")
        counter = 0
        out = ""
        while counter < 20 and counter < len(lines):
            line = lines[counter]
            counter += 1
            if line.strip() == "" and counter > 10:
                return out
            if len(line) > 0 and line.strip()[0] == "#" and counter > 4:
                return out
            out += "%s\n" % line
        return out

    def _data_update(self, data):
        res = {}
        for key, val in self.data.items():
            if key in data:
                valUpdate = copy.copy(data[key])
                if j.data.types.list.check(val):
                    if not j.data.types.list.check(valUpdate):
                        raise j.exceptions.Input(
                            message="(%s)\nerror in data structure, list should match list" %
                            self, level=1, source="", tags="", msgpub="")
                    for item in valUpdate:
                        if item not in val and item != "":
                            val.append(item)
                    self.data[key] = val
                else:
                    self.data[key] = valUpdate
        for key, valUpdate2 in data.items():
            # check for the keys not in the self.data yet and add them, the others are done above
            if key not in self.data:
                self.data[key] = copy.copy(valUpdate2)  # needs to be copy.copy otherwise we rewrite source later

    def _data_default_process(self):
        """
        empty data, go over default data's and update in self.data
        """
        self.data = {}
        keys = [item for item in self.docsite.data_default.keys()]
        keys.sort(key=len)
        for key in keys:
            key = key.strip("/")
            if self.path_rel.startswith(key):
                data = self.docsite.data_default[key]
                self._data_update(data)
        print("data process doc")
        from IPython import embed;embed(colors='Linux')
        s

    def _macro_process(self,methodline,block):
        """
        eval the macro
        """
        methodcode = methodline[3:]
        methodcode = methodcode.rstrip(", )")  # remove end )
        methodcode = methodcode.replace("(", "(self,")
        if not methodcode.strip() == line[3:].strip():
            # means there are parameters
            methodcode += ",content=block)"
        else:
            methodcode += "(content=block)"
        methodcode = methodcode.replace(",,", ",")

        if methodcode.strip()=="":
            raise RuntimeError("method code cannot be empty")

        cmd = "j.tools.docgenerator.macros." + methodcode
        # self.logger.debug(cmd)
        # macro = eval(cmd)
        try:
            macro = eval(cmd) #is the result of the macro which is returned
        except Exception as e:
            from IPython import embed;embed(colors='Linux')
            s
            block = "```python\nERROR IN MACRO*** TODO: *1 ***\ncmd:\n%s\nERROR:\n%s\n```\n" % (cmd, e)
            self.docsite.error_raise(block, doc=self)          
        return macro

    def _links_process(self):
        
        # check links for internal images
        return

        ws = "wiki/" + self.docsite.name

        regex = "\] *\([a-zA-Z0-9\.\-\_\ \/]+\)"  # find all possible images/links
        for match in j.data.regex.yieldRegexMatches(regex, self.content, flags=0):
            self.logger.debug("##:file:link:%s" % match)
            fname = match.founditem.strip("[]").strip("()")
            if match.founditem.find("/") != -1:
                fname = fname.split("/")[1]
            if j.sal.fs.getFileExtension(fname).lower() in ["png", "jpg", "jpeg", "mov", "mp4"]:
                fnameFound = self.docsite.file_get(fname, die=False)
                if fnameFound==None:
                    print("links process")
                    from IPython import embed;embed(colors='Linux')
                    s
                    msg = "**ERROR: COULD NOT FIND LINK: %s TODO: **" % fnameFound
                    self.content = self.content.replace(match.founditem, msg)
                else:
                    self.content = self.content.replace(match.founditem, "](/%s/files/%s)" % (self.docsite.name, fnameFound))
            elif j.sal.fs.getFileExtension(fname).lower() in ["md"]:
                shortname = fname.lower()[:-3]
                if shortname not in self.docsite.docs:
                    msg = "**ERROR: COULD NOT FIND LINK: %s TODO: **" % shortname
                    self.docsite.error_raise(msg, doc=self)
                    self.content = self.content.replace(match.founditem, msg)
                else:
                    thisdoc = self.docsite.docs[shortname]
                    self.content = self.content.replace(match.founditem, "](%s)" % (thisdoc.url))

        regex = "src *= *\" */?static"
        for match in j.data.regex.yieldRegexMatches(regex, self.content, flags=0):
            self.content = self.content.replace(match.founditem, "src = \"/")

    def render(self,**args):
        """
        render markdown content using jinja2
        """
        return j.tools.jinja2.text_render(self.content,doc=self,**args)

    def __repr__(self):
        return "doc:%s:%s" % (self.name, self.path)

    __str__ = __repr__


