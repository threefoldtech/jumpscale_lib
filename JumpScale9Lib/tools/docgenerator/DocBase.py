from js9 import j
import toml

import copy

JSBASE = j.application.jsbase_get_class()


class DocBase(JSBASE):
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


    @property
    def template(self):
        
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        j2_env = Environment(
            loader = FileSystemLoader(self.path_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = j2_env.get_template('%s.%s'%(self.name_original,self.extension))  
        return template
        


    def __repr__(self):
        return "doc:%s:%s" % (self.name, self.path)

    __str__ = __repr__
