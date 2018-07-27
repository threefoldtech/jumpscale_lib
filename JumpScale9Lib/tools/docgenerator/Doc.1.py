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
        
        self.path_dir = j.sal.fs.getDirName(self.path)
        self.path_dir_rel = j.sal.fs.pathRemoveDirPart(self.path_dir, self.docsite.path).strip("/")
        self.name = j.data.text.strip_to_ascii_dense(name)
        self.name_original = name
        self.path_rel = j.sal.fs.pathRemoveDirPart(path, self.docsite.path).strip("/")

        name_dot =  "%s/%s" % (self.path_dir_rel,name)
        self.name_dot = name_dot.replace("/",".")
        self.name_dot_lower = self.name_dot.replace("/",".").lower().strip(".")

        self.content = ""
        self.show = True
        self.errors = []

        if j.sal.fs.getDirName(self.path).strip("/").split("/")[-1][0] == "_":
            # means the subdir starts with _
            self.show = False

        self._processed = False

        self._extension = None

        self._content_default = ""
        self.data = {} #is all data, from parents as well, also from default data
        self.metadata = {}  #is the data which is in the page itself

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
    def url(self):
        
        rpath = self.path_rel[:-3]
        rpath += '/'
        return "%s%s" % (self.docsite.sitepath, rpath)

    @property
    def content_clean(self):

        # remove the code blocks (comments are already gone)
        state = "start"
        out = ""
        for line in self.content.split("\n"):
            if state == "blockstart":
                if (line.startswith("```") or line.startswith("'''")):
                    # end of block
                    state = "start"
                continue

            if state == "start" and (line.startswith("```") or line.startswith("'''")):
                state = "blockstart"
                continue

            out += "%s\n" % line
        out = out.replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
        return out

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

    @property
    def content_default(self):
        """
        TODO:*1 need to describe how this works with default content
        """
        if self._content_default == "":
            keys = [item for item in self.docsite.content_default.keys()]
            keys.sort(key=len)
            C = ""
            for key in keys:
                key = key.strip("/")
                if self.path_rel.startswith(key):
                    C2 = self.docsite.content_default[key]
                    if len(C2) > 0 and C2[-1] != "\n":
                        C2 += "\n"
                    C += C2
            self._content_default = C
        return self._content_default

    def _metadata_process(self, dataText):
        try:
            data = j.data.serializer.toml.loads(dataText)
        except Exception as e:
            self.logger.debug("DEBUG NOW toml load issue in doc")
            from IPython import embed
            embed()
            raise RuntimeError("stop debug here")
        self._metadata_update(data)
        return data

    def _metadata_update(self, data):
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
                self._metadata_update(data)

    def _methodline_process(self,line,block):
        methodcode = line[3:]
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
        # block = eval(cmd)
        try:
            block = eval(cmd)
        except Exception as e:
            from IPython import embed;embed(colors='Linux')
            s
            block = "```python\nERROR IN MACRO*** TODO: *1 ***\ncmd:\n%s\nERROR:\n%s\n```\n" % (cmd, e)
            self.docsite.error_raise(block, doc=self)          
        return block

    def _block_process(self,out,block,language_type):
        """
        is a code block

        can be std code e.g. python code (then will just return it how it was)

        """

        if len(block.strip())==0:
            return out

        splitted = block.split("\n")
        line0 = splitted[0]

        if language_type.lower() == "meta":
            self.metadata = self._metadata_process(block)
            block = ""
        elif line0.strip()=="!!!":   
            block = "\n".join(splitted[1:])
            self.metadata = self._metadata_process(block)
            block = ""
        elif line0.startswith("!!!"):        
            #means is macro  
            block = "\n".join(splitted[1:])    
            out += self._methodline_process(line0,block)

        else:
            #is a normal code block so will add to out again
            out+="\n```%s\n%s\n```\n" % (language_type,block)

        return out 

    def _content_single_line_macros(self):
        """
        look for '!!! at start of line, this is a single line macro
        """
        out=""
        for line in self.content.split("\n"):
            if line.strip().startswith("!!!"):                
                line2 = line.strip()[3:]
                if line2.strip()=="":
                    raise RuntimeError("line !!! should not be empty at this point")
                line = self._methodline_process(line,block="")
            out += "%s\n"%line
        self.content = out

    def _content_blocks_process(self):
        """
        look for ''' ... ''' and then process, can be macro or real code block
        """
        # j.tools.docgenerator.logger.info("process:%s" % self)
        content = self.content

        # process multi line blocks
        state = "start"
        block = ""
        out = ""
        codeblocks = []
        dataBlock = ""
        language_type = ""
        for line in content.split("\n"):
            line2=line.strip()
            
            if state == "blockstart" and (line2.startswith("```") or line2.startswith("'''")):
                #means we are at end of block
                out = self._block_process(out,block,language_type)
                block = ""
                state = "start"
                language_type = ""
                continue

            if state == "blockcomment":
                if line.startswith("-->"):
                    # end of comment
                    state = "start"
                continue

            if state == "blockstart":
                block += "%s\n" % line
                continue

            if state == "start" and (line2.startswith("```") or line2.startswith("'''")):
                language_type = line[3:].strip()
                state = "blockstart"
                continue

            self.logger.debug(line)
            if state == "start" and (line.startswith("<!-")):
                state = "blockcomment"
                continue

            out += "%s\n" % line
        
        #only the last data block will be remembered
        out = self._block_process(out,block,language_type)  

        self.content = out

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

    def _defs_process(self):
    
        def ssplit(name):
            for item in " {[]}(),;:./?\"'$%^&*=!":
                if item in name:
                    name = name.split(item)[0]
            return name

        regex = "\$\$.*"  # find all possible defs
        for match in j.data.regex.yieldRegexMatches(regex, self.content, flags=0):
            # self.logger.debug("##:%s" % match)
            defname = match.founditem
            defname0 = ssplit(defname.replace("$", ""))
            defname = j.data.text.strip_to_ascii_dense(defname0)
            if defname in self.docsite.defs:
                def_ = self.docsite.defs[defname]
                defnew = "[%s](%s:%s.md)" % (def_.nameOriginal, def_.docsite.name, def_.nameOriginal)
                self.content = self.content.replace("$$" + defname0, defnew)
            else:
                defnew = "**ERROR: COULD NOT FIND DEF: %s**" % defname
                self.content = self.content.replace("$$" + defname0, defnew)
                self.docsite.error_raise(defnew, doc=self)

        self.process3()

    def process(self):
        if self._processed:
            return 

        j.tools.docgenerator.logger.info("process:%s" % self)

        if self.content_default != "":
            self.content = self.content_default
            if self.content[-1] != "\n":
                self.content += "\n"

        self.content += j.sal.fs.fileGetContents(self.path)
        
        self._data_default_process()

        self._content_blocks_process()

        if "!!!" in self.content:
            #means there are still macro's in there, need to check per line
            self._content_single_line_macros()

        # self._data_add()

        if "{{" in self.content:
            self.content = self.template.render(obj=self)

        self._links_process()
        # self._defs_process()

        self._processed = True

    def template_render(self,**args):
        return j.tools.jinja2.file_render(self.path,write=False,dest=None,**args)

    def __repr__(self):
        return "doc:%s:%s" % (self.name, self.path)

    __str__ = __repr__


    # def write(self):

    #     if self.show and self.docsite.config:
    #         if self.errors != []:
    #             if "tags" not in self.data:
    #                 self.data["tags"] = ["error"]
    #             else:
    #                 self.data["tags"].append("error")

    #         C = ""

    #         if self.docsite.hugo and self.doc_add_meta:
    #             C += "+++\n"
    #             C += toml.dumps(self.data)
    #             C += "\n+++\n\n"

    #         C += self.content

    #         dpath = j.sal.fs.joinPaths(self.docsite.outpath, "content", self.path_rel)
    #         j.sal.fs.createDir(j.sal.fs.getDirName(dpath))
    #         j.sal.fs.writeFile(filename=dpath, contents=C)




    # def _data_add(self):
    #     """
    #     looks if default data like tags, date & title filled in, if not will add to metadata & rewrite in content
    #     """
        
    #     rewriteDataBlock = False

    #     if "title" not in self.metadata:
    #         rewriteDataBlock = True
    #         name = self.name_original.replace("_", " ").replace("-", " ").strip()
    #         # makes first letters uppercase
    #         name = " ".join([item[0].upper() + item[1:] for item in name.split(" ")])
    #         self.metadata["title"] = name
    #     if "date" not in self.metadata:
    #         rewriteDataBlock = True
    #         self.metadata["date"] = j.data.time.epoch2HRDate(j.data.time.epoch).replace("/", "-")
    #     if "tags" not in self.metadata:
    #         parts = [item.lower() for item in j.sal.fs.getDirName(self.path).strip("/").split("/")[-4:]]
    #         tags = []
    #         if "defs" in parts or "def" in parts:
    #             tags.append("def")
    #         if "howto" in parts or "howtos" in parts:
    #             tags.append("howto")
    #         if "ideas" in parts or "idea" in parts:
    #             tags.append("idea")
    #         if "question" in parts or "questions" in parts:
    #             tags.append("question")
    #         if "spec" in parts or "specs" in parts:
    #             tags.append("spec")
    #         if "overview" in parts:
    #             tags.append("overview")
    #         if "api" in parts or "apis" in parts:
    #             tags.append("api")
    #         self.metadata["tags"] = tags
    #         rewriteDataBlock = True

        #LETS NOT REWRITE THE DATABLOCK< THINK BAD (despiegk)

        # if rewriteDataBlock:
        #     content0 = j.sal.fs.fileGetContents(self.path)
        #     content1 = "\n```meta\n"
        #     content1 += j.data.serializer.toml.dumps(self.metadata)
        #     content1 += "```\n"
        #     self._processData(j.data.serializer.toml.dumps(self.metadata))
        #     j.sal.fs.writeFile(filename=self.path, contents=content0 + content1)
        #     out += content1

    # def _links_process(self):
        
    #     # check links for internal images

    #     ws = j.tools.docgenerator.webserver + self.docsite.name

    #     regex = "\] *\([a-zA-Z0-9\.\-\_\ \/]+\)"  # find all possible images/links
    #     for match in j.data.regex.yieldRegexMatches(regex, self.content, flags=0):
    #         self.logger.debug("##:file:link:%s" % match)
    #         fname = match.founditem.strip("[]").strip("()")
    #         if match.founditem.find("/") != -1:
    #             fname = fname.split("/")[1]
    #         if j.sal.fs.getFileExtension(fname).lower() in ["png", "jpg", "jpeg", "mov", "mp4"]:
    #             fnameFound = self.docsite.file_get(fname, die=False)
    #             if fnameFound==None:
    #                 print("links process")
    #                 from IPython import embed;embed(colors='Linux')
    #                 s
    #                 msg = "**ERROR: COULD NOT FIND LINK: %s TODO: **" % fnameFound
    #                 self.content = self.content.replace(match.founditem, msg)
    #             else:
    #                 self.content = self.content.replace(match.founditem, "](/%s/files/%s)" % (self.docsite.name, fnameFound))
    #         elif j.sal.fs.getFileExtension(fname).lower() in ["md"]:
    #             shortname = fname.lower()[:-3]
    #             if shortname not in self.docsite.docs:
    #                 msg = "**ERROR: COULD NOT FIND LINK: %s TODO: **" % shortname
    #                 self.docsite.error_raise(msg, doc=self)
    #                 self.content = self.content.replace(match.founditem, msg)
    #             else:
    #                 thisdoc = self.docsite.docs[shortname]
    #                 self.content = self.content.replace(match.founditem, "](%s)" % (thisdoc.url))

    #     regex = "src *= *\" */?static"
    #     for match in j.data.regex.yieldRegexMatches(regex, self.content, flags=0):
    #         self.content = self.content.replace(match.founditem, "src = \"/")
