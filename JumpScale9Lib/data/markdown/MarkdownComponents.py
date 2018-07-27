from js9 import j
import mistune


class MDBase():
    

    def __repr__(self):
        out = self.text
        if len(out) > 0:
            if out[-1] != "\n":
                out += "\n"
            if out[-2] != "\n":
                out += "\n"
        return out

    @property
    def markdown(self):
        return str(self)

    @property
    def html(self):
        return mistune.markdown(self.text, escape=True, hard_wrap=True)

    __str__ = __repr__

class MDTable(MDBase):

    def __init__(self):
        self.header = []
        self.rows = []
        self.type = "table"

    def rows_as_objects(self):
        nrcols=len(self.header)
        res=[]
        for row in self.rows:
            oo = object()
            for x in range(nrcols):
                val=row[x]
                if val.strip()==".":
                    val=""
                else:
                    try:
                        val=int(val)
                    except:
                        pass
                key=self.header[x]
                oo.__dict__[key]=val
            res.append(oo)
        return res


    def header_add(self, cols):
        """
        cols = columns can be comma separated string or can be list
        """
        if j.data.types.string.check(cols):
            cols=[item.strip().strip("'").strip('"').strip() for item in cols.split(",")]

        self.header = cols
        for nr in range(len(self.header)):
            if self.header[nr] is None or self.header[nr].strip() == "":
                self.header[nr] = " . "

    def row_add(self, cols):
        """
        cols = columns  can be comma separated string or can be list
        """        
        if j.data.types.string.check(cols):
            cols=[item.strip().strip("'").strip('"').strip() for item in cols.split(",")]
        if len(cols) != len(self.header):
            raise j.exceptions.Input(
                "cols need to be same size as header. %s vs %s" % (len(cols), len(self.header)))
        for nr in range(len(cols)):
            if cols[nr] is None or str(cols[nr]).strip() == "":
                cols[nr] = " . "
        self.rows.append(cols)

    def _findSizes(self):
        m = [0 for item in self.header]
        x = 0
        for col in self.header:
            if len(col) > m[x]:
                m[x] = len(col)
            x += 1
        for row in self.rows:
            x = 0
            for col in row:
                col=str(col)
                if len(col) > m[x]:
                    m[x] = len(col)
                    if m[x]<3:
                        m[x]=3
                x += 1
        return m

    @property
    def text(self):        
        return str(self)

    def __repr__(self):
        def pad(text, l, add=" "):
            if l<4:
                l=4
            text=str(text)
            while(len(text) < l):
                text += add
            return text
        pre = ""
        m = self._findSizes()

        # HEADER
        x = 0
        out = "|"
        for col in self.header:
            col = pad(col, m[x])
            out += "%s|" % col
            x += 1
        out += "\n"

        # INTERMEDIATE
        x = 0
        out += "|"
        for col in self.header:
            col = pad("", m[x], "-")
            out += "%s|" % col
            x += 1
        out += "\n"

        for row in self.rows:
            x = 0
            out += "|"
            for col in row:
                col = pad(col, m[x])
                out += "%s|" % col
                x += 1
            out += "\n"

        out += "\n"
        return out

    __str__ = __repr__


class MDHeader(MDBase):

    def __init__(self, level, title):
        self.level = level
        self.title = title
        self.type = "header"
        

    def __repr__(self):
        pre = ""
        for i in range(self.level):
            pre += "#"
        return "%s %s" % (pre, self.title)

    __str__ = __repr__

    @property
    def text(self):        
        return str(self)

class MDListItem(MDBase):

    def __init__(self, level, text):
        self.level = level
        self.text = text
        self.type = "list"
        

    def __repr__(self):
        pre = ''
        if self.level > 1:
            pre = '    ' * (self.level - 1)
        return "%s%s" % (pre, self.text)

    __str__ = __repr__


class MDComment(MDBase):

    def __init__(self, text):
        self.text = text
        self.type = "comment"
        

    def __repr__(self):
        out = "<!--\n%s\n-->\n" % self.text

    __str__ = __repr__


class MDComment1Line(MDBase):

    def __init__(self, text):
        self.text = text
        self.type = "comment1line"
        

    def __repr__(self):
        out = "<!--%s-->\n" % self.text
        return out

    __str__ = __repr__


class MDBlock(MDBase):

    def __init__(self, text):
        self.text = text
        self.type = "block"
        

    def __repr__(self):
        out = self.text
        if len(out) > 0:
            if out[-1] != "\n":
                out += "\n"
            if out[-2] != "\n":
                out += "\n"
        return out


    __str__ = __repr__


class MDCodeMacroDataBase():

    @property
    def markdown(self):
        return str(self)        

    @property
    def html(self):
        return "<code>\n\n%s\n</code>\n\n"%self.text    

    
class MDCode(MDCodeMacroDataBase):

    def __init__(self, text, lang):
        self.text = text
        self.type = "code"
        self.lang = lang
        self.method = ""
        
    def __repr__(self):        
        out = "```%s\n"%self.lang
        out += self.text.strip()
        out += "\n```\n"
        return out

    __str__ = __repr__


class MDMacro(MDCodeMacroDataBase):

    def __init__(self, data="", lang="", method=""):
        self.text = data
        self.lang = lang
        self.type = "macro"
        self.method = method.strip()

    def __repr__(self):
        out = "```%s\n!!!%s\n"%(self.lang,self.method)
        t = self.text.strip()
        out += t
        if t:
            out+="\n"
        out += "```\n"
        return out

    __str__ = __repr__


class MDData(MDCodeMacroDataBase):

    def __init__(self, ddict={},toml="",yaml=""):
        
        self.type = "data"

        self._toml = toml
        self._yaml = yaml
        self._ddict = ddict
        
        self._hash = ""

    @property
    def datahr(self):
        return j.data.serializer.toml.dumps(self.ddict)

    @property
    def toml(self):
        if self._toml:
            return self._toml
        else:
            return j.data.serializer.toml.dumps(self.ddict)

    @property
    def ddict(self):
        if self._toml:
            return j.data.serializer.toml.loads(self._toml)
        elif self._yaml:
            return j.data.serializer.yaml.loads(self._yaml)
        elif self._ddict is not {}:            
            return  self._ddict
        else:
            RuntimeError ("toml or ddict needs to be filled in in data object")

    @property
    def text(self):
        if self._toml:            
            return self._toml
        elif self._yaml:
            out = "```yaml\n!!!data\n"  #need new header
            return self._yaml
        else:    
            return self.toml

    @property
    def hash(self):
        if self._hash == "":
            json = j.data.serializer.json.dumps(self.ddict, True, True)
            self._hash = j.data.hash.md5_string(json)
        return self._hash

    def __repr__(self):
        
        out = "```toml\n!!!data\n"
        out += self.text.strip()
        out += "\n```\n"
        return out

    __str__ = __repr__

# class Object(MDBase):
#     def __init__(self):
#         pass


#     def __str__(self):
#         out=""
#         for key,val in self.__dict__.items():
#             out+="%s:%s "%(key,val)
#         out=out.strip()
#         return out

#     __repr__ = __str__

