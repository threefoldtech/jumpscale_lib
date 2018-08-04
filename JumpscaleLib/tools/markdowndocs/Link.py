from jumpscale import j
import toml

import copy

JSBASE = j.application.jsbase_get_class()

class Link(JSBASE):
    def __init__(self,doc, source):
        JSBASE.__init__(self)        
        self.docsite = doc.docsite
        self.doc = doc
        self.source = source #original text
        self.cat = ""  #category in image,doc,link,officedoc, imagelink  #doc is markdown
        self.link_source = "" #text to replace when rewrite is needed
        self.link_source_original = "" #original link
        self.error_msg = ""
        self.filename = ""
        self.filepath = ""
        self.link_descr="" #whats inside the []
        self.link_to_doc = None
        self._process()

    def _clean(self,name):
        return j.data.text.strip_to_ascii_dense(name)        

    def error(self,msg):
        self.error_msg = msg
        msg="**ERROR:** problem with link:%s\n%s"%(self.source,msg)        
        # self.logger.error(msg)
        self.docsite.error_raise(msg, doc=self.doc)
        self.doc._content = self.doc._content.replace(self.source,msg) 
        return msg

    def _process(self):
        self.link_source = self.source.split("(",1)[1].split(")",1)[0] #find inside ()
        self.link_descr = self.source.split("[",1)[1].split("]",1)[0] #find inside []
        
        if "@" in self.link_descr:
            self.link_source_original = self.link_descr.split("@")[1].strip() #was link to original source
            self.link_descr = self.link_descr.split("@")[0].strip()
            
        self.extension = j.sal.fs.getFileExtension(self.link_source)

        if "http" in self.link_source:
            self.link_source_original = self.link_source            
            name = ""
            if self.source.startswith("!"):
                if not self.extension in ["png", "jpg", "jpeg", "mov", "mp4"]:
                    self.extension = "jpeg" #to support url's like https://images.unsplash.com/photo-1533157961145-8cb586c448e1?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=4e252bcd55caa8958985866ad15ec954&auto=format&fit=crop&w=1534&q=80
                else:
                    name = j.sal.fs.getBaseName(self.source,removeExtension=True)

                self.logger.info("image download")
                c=j.clients.http.getConnection()
                link_descr = self._clean(self.link_descr)
                if len(link_descr)>0:
                    name = link_descr
                
                if name.endswith(".%s"%self.extension):
                    name = ".".join(name.split(".")[:-1]) #remove extension

                if name == "":
                    name,dest = self.doc._get_file_path_new(extension=self.extension)
                else:            
                    dest = "%s/%s.%s"%(self.doc.path_dir,name,self.extension)

                self.link_source = "%s.%s"%(name,self.extension) #will be replaced with this name
                
                self.logger.info("download:%s"%self.link_source_original)
                c.download(self.link_source_original,dest)
                self.replace_in_doc()
                self.logger.info ("download done")
            else:
                #check link exists
                self.cat = "link"
                if self.docsite.links_verify:
                    self.link_verify()
         
        else:

            if self.link_source.find("/") != -1:
                name = self.link_source.split("/")[-1]     
            else:
                name = self.link_source

            #now we have clean name with no " and ' and spaces around and only basename

            self.filename = self._clean(name) #cleanly normalized name but extension still part of it
            #e.g. balance_inspiration_motivation_life_scene_wander_big.jpg
            self.extension = j.sal.fs.getFileExtension(self.filename)

            #only possible for images (video, image)
            if self.source.startswith("!"):
                self.cat = "image"
                if not self.extension in ["png", "jpg", "jpeg", "mov", "mp4"]:
                    return self.error("found unsupported image file")

            if self.cat =="":
                if self.extension in ["png", "jpg", "jpeg", "mov", "mp4"]:
                    self.cat = "imagelink"
                elif self.extension in ["doc", "docx", "pdf", "xls", "xlsx", "pdf"]:
                    self.cat = "officedoc"
                elif self.extension in ["md","",None]:
                    self.cat = "doc" #link to a markdown document
                    self.link_to_doc =  self.docsite.doc_get(self.filename ,die=False)
                    if self.link_to_doc==None:
                        return self.error("COULD NOT FIND LINK: %s TODO: **" % self.filename )
                    return
                else:
                    return self.error("found unsupported extension")
            

            self.filepath = self.doc.docsite.file_get(self.filename, die=False)
            if self.filepath is None:
                return self.error("could not find file in docsite")
                
    
    @property
    def markdown(self):
        if self.source.startswith("!"):
            c="!"
            if self.link_source_original is not "":
                descr="%s@%s"%(self.link_descr,self.link_source_original )
            else:
                descr=self.link_descr
        else:
            c=""
            descr=self.link_descr
        c+= "[%s](%s)"%(descr,self.link_source)
        return c

    def link_verify(self):
        def do():
            self.logger.info("check link exists:%s"%self.link_source)
            c=j.clients.http.getConnection()
            try:
                resp = c.get(self.link_source)
            except Exception as e:
                if "unauthorized" in str(e).lower():
                    return True #is not error, means there is answer
                raise e
            if resp.status is not 200:
                return "broken link"
            return True                 
        res =  self.cache.get(self.link_source, method=do, expire=3600)
        if res is not True:
            return self.error(res)

    def replace_in_doc(self):
        self.logger.info("replace_in_doc")
        self.doc._content = self.doc._content.replace(self.source,self.markdown)   
        self.source = self.markdown #there is a new source now        
        self.doc.docsite._files[self.filename]=self.link_source #need to register file in docsite
        j.sal.fs.writeFile(self.doc.path,self.doc._content)
        self._process()

    def __repr__(self):
        if self.cat == "link":
            return "link:%s:%s" % (self.cat, self.link_source)
        else:
            return "link:%s:%s" % (self.cat, self.filename)

    __str__ = __repr__

