from js9 import j
from .MarkdownComponents import *
JSBASE = j.application.jsbase_get_class()
import copy
import mistune

class MarkdownDocument(JSBASE):

    def __init__(self, content="", path=""):
        JSBASE.__init__(self)
        if path != "":
            content = j.sal.fs.fileGetContents(path)

        self._content = content

        self.items = []
        if self._content:
            self._parse()

    def table_add(self):
        """
        returns table which needs to be manipulated
        """
        t = MDTable()
        self.items.append(t)
        return t

    def header_add(self, level, title):
        """
        """
        self.items.append(MDHeader(level, title))

    def listitem_add(self, level, text):
        """
        """
        self.items.append(MDListItem(level, text))

    def comment_add(self, text):
        """
        """
        self.items.append(MDComment(text))

    def comment1line_add(self, text):
        """
        """
        self.items.append(MDComment1Line(text))

    def block_add(self, text):
        """
        """
        self.items.append(MDBlock(text))

    def code_add(self, text, lang):
        """
        """
        self.items.append(MDCode(text, lang=lang))

    def data_add(self, ddict=None, toml="", yaml=""):
        if ddict is None:
            ddict = {}
        ddict = copy.copy(ddict)
        self.items.append(MDData(ddict=ddict,toml=toml,yaml=yaml))

    def macro_add(self, method, data="",lang=""):
        self.items.append(MDMacro(method=method, data=data, lang=lang))        

    def _parse(self):

        state = ""
        block = ""

        #needed to calculate the level of the lists
        prevListLevel = 0
        curListLevel = 1


        listblocklines = []
        # substate = ""

        def block_add(block):
            if block.strip() != "":
                self.block_add(block)
            substate = ""
            state = ""
            return ""

        if not self.content or self.content.strip() == '':
            return

        for line in self.content.split("\n"):
            # HEADERS
            if line.startswith("#") and state == "":
                block = block_add(block)
                level = 0
                line0 = line
                while line0.startswith("#"):
                    level += 1
                    line0 = line0[1:]
                title = line0.strip()
                self.items.append(MDHeader(level, title))
                continue

            linestripped = line.strip()

            if linestripped.startswith("<!--") and linestripped.endswith("-->") and state == "":
                comment_part = linestripped[4:-3].strip()
                self.comment1line_add(comment_part)
                block = ""
                state = ""
                continue

            if line.startswith("!!!") and state == "": #is 1 line macro
                lang = ""
                self.codeblock_add(line,lang=lang)
                continue

            if line.startswith("<!-"):
                state = "COMMENT"
                continue

            # process all comment states
            if state.startswith("COMMENT"):
                if line.startswith("-->"):
                    state = ""
                    if state == "COMMENT":
                        self.items.append(MDComment(block))
                    block = ""
                    continue
                block += "%s\n" % line

            # LIST
            if linestripped.startswith("-") or linestripped.startswith("*") and state in ["","LIST"]:
                state = "LIST"
                listblocklines.append(line)
                continue
            else:
                # get out of state state
                if state == "LIST":
                    state = ""
                    self.items.append(MDList("\n".join(listblocklines)))
                    listblocklines = [] 

            if state == "TABLE" and not linestripped.startswith("|"):
                state = ""
                self.items.append(table)
                table = None
                cols = []

            # TABLE
            if state != "TABLE" and linestripped.startswith("|"):
                state = "TABLE"
                block = block_add(block)
                cols = [item.strip()
                        for item in line.split("|") if item.strip() != ""]
                table = MDTable()
                table.header_add(cols)
                continue

            if state == "TABLE":
                if linestripped.startswith("|") and linestripped.endswith("|") and line.find("---") != -1:
                    continue
                cols = [item.strip() for item in line.strip().strip('|').split("|")]
                table.row_add(cols)
                continue

            # CODE
            if state == "" and linestripped.startswith("```") or linestripped.startswith("'''"):
                block = block_add(block)
                state = "CODE"
                lang = line.strip("'` ")
                continue

            if state == "CODE":
                if linestripped.startswith("```") or linestripped.startswith("'''"):
                    # import pudb; pudb.set_trace()
                    state = ""
                    self.codeblock_add(block,lang=lang)
                    block = ""
                    lang = ""
                else:
                    block += "%s\n" % line
                continue

            if linestripped != "":
                block += "%s\n" % line
            block = block_add(block)

        # from IPython import embed;embed(colors='Linux')

    def codeblock_add(self,block,lang=""):
        """
        add the full code block
        """
        lang=lang.lower().strip()
        if block.strip().split("\n")[0].lower().startswith("!!!data"):
            #is data
            block="\n".join(block.strip().split("\n")[1:])+"\n"
            if lang=="" or lang=="toml":
                self.data_add(toml=block)
            elif lang=="yaml":
                self.data_add(yaml=block)
            else:
                raise RuntimeError("could not add codeblock for %s"%block)            
        elif block.strip().split("\n")[0].startswith("!!!"):
            #is macro
            method=block.strip().split("\n")[0][3:].strip() #remove !!!
            data="\n".join(block.strip().split("\n")[1:])+"\n"
            self.macro_add(method=method,data=data,lang=lang)
        else:
            self.code_add(text=block,lang=lang)

    @property
    def content(self):
        return self._content


    def __repr__(self):
        out = ""
        prevtype = ""
        for item in self.items:
            if item.type not in ["list"]:
                if prevtype == "list":
                    out += "\n"
                out += str(item).strip() + "\n\n"
            else:
                out += str(item).rstrip() + "\n"

            prevtype = item.type
        return out

    __str__ = __repr__

    def get_first(self,categories=["block"]):
        for item in self.items:
            if item.type in categories:
                return item

    @property
    def markdown(self):
        return str(self)

    @property
    def html(self):
        out="""
        <!DOCTYPE html>
        <html>
        <body>
        """
        out=j.data.text.strip(out)
        for item in self.items:
            out+= item.html +"\n"
        out+="\n</body>\n</html>\n"
        return out

    def htmlpage_get(self,htmlpage=None, webparts=True):
        """
        is the htmlpage, if not specified then its j.data.html.page_get()

        if webparts it will get them from https://github.com/Jumpscale/web_libs/tree/master/webparts

        """
        if webparts:
            j.data.html.webparts_enable()
        if not htmlpage:
            htmlpage = j.data.html.page_get()

        for item in self.items:
            if item.type=="block":
                htmlpage.paragraph_add(mistune.markdown(item.text.strip()))
            elif item.type=="header":
                htmlpage.header_add(item.title,level= item.level)
            elif item.type=="code":
                # codemirror code generator                
                j.data.html.webparts.codemirror_add(self=htmlpage,code=item.text)
            elif item.type=="table":
                #can also use htmlpage.table_add  #TODO: need to see whats best
                htmlpage.html_add(item.html) #there will be more optimal ways how to do this in future, with real javascript                
            elif item.type=="data":
                pass
            elif item.type=="list":
                htmlpage.html_add(mistune.markdown(item.text))
            elif item.type=="macro":
                if j.tools.docgenerator._macros_loaded is not []:
                    #means there is no doc generator so cannot load macro
                    j.data.html.webparts.codemirror_add(self=htmlpage,code=item.text)
                else:
                    print("html_get from markdown, need to execute macro")
                    from IPython import embed;embed(colors='Linux')
                    s
            else:
                print("htmlpage_get")
                from IPython import embed;embed(colors='Linux')
                s
        return htmlpage
            


    # def _findFancyHeaders(self):
    #     if not self.content or self.content.strip() == "":
    #         return
    #     out = []
    #     for line in self.content.split("\n"):
    #         if line.startswith("===="):
    #             out[-1] = "# %s" % out[-1]
    #             continue

    #         if line.startswith("-----"):
    #             out[-1] = "## %s" % out[-1]
    #             continue
    #         out.append(line)

    #     self._content = "\n".join(out)


        # def dataobj_get(self, ttype, guid):
    #     """
    #     ttype is name for the block
    #     guid is unique id, can be name or guid or int(id)

    #     """
    #     key = "%s__%s" % (ttype, guid)
    #     if key not in self._dataCache:
    #         self.datacollection_get()
    #     if key not in self._dataCache:
    #         raise j.exceptions.Input(
    #             "Cannot find object with type:%s guid:%s" % (ttype, guid))
    #     return self._dataCache[key].ddict

    # @property
    # def tokens(self):
    #     if self._tokens == "":
    #         bl = BlockLexer()
    #         self._tokens = bl.parse(self._content)
    #     return self._tokens

    # @tokens.setter
    # def tokens(self, val):
    #     self._changed_tokens = True
    #     self._tokens = val
