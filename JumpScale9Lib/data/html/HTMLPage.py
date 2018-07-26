from js9 import j
# import copy

JSBASE = j.application.jsbase_get_class()


class HTMLPage(JSBASE):

    """
    the methods add code to the self.body part !!!!!
    """

    def __init__(self, ):
        """
        """
        self.content = ""

        # self.currentlinenr = len(self.content.split("\n")) + 1
        # self.actions = {}
        # self.parent = parent

        self.libs = ""
        self.body = ""

        self.scriptBody = ""
        self.jscsslinks = {}
        self.divlevel = []

        self._inBlock = False
        self._inBlockType = ""
        self._inBlockClosingStatement = ""
        self._bulletslevel = 0
        self._codeblockid = 0

        self.padding = True

        # self.pagemirror4jscss = None

        self.processparameters = {}
        self.bodyattributes = []

        self.liblocation = "/static/"
        
        # self._hasCharts = False
        # self._hasCodeblock = False
        # self._hasSidebar = False
        
        # self.functionsAdded = {}
        self._explorerInstance = 0
        self._lineId = 0
        # self.documentReadyFunctions = []


    def addPart(self, part, newline=False, isElement=True, blockcheck=True):
        if blockcheck:
            # print "blockcheck %s" % part
            self._checkBlock("", "", "")
        # else:
            # print "no blockcheck %s" % part
        part = str(part)
        part = part.replace("text:u", "")
        part.strip("'")
        part = part.strip()
        part = part.replace("\r", "")
        if part != '' and isElement:
            part = "%s" % part
        elif newline and part != '':
            part = "<p>%s</p><br/>" % part
        elif newline and part == '':
            part = '<br/>'
        elif part == "":
            pass
        else:
            part = "<p>%s</p>" % part

        part = part.replace("&lt;br&gt;", "<br />")

        if part != "":
            self.body = "%s%s\n" % (self.body, part)

    def addParagraph(self, part):
        self.addPart(part, isElement=False)

    # def addFavicon(self, href, type):
    #     self.favicon = '<link rel="shortcut icon" type="%s" href="%s" />' % (type, href)

    def addBullet(self, part, level=1, bullet_type='bullet', tag='ul', attributes=''):
        self._checkBlock(bullet_type, "", "</{0}>".format(tag))
        if level > self._bulletslevel:
            for i in range(level - self._bulletslevel):
                self.addPart("<{0} {1}>".format(tag, attributes), blockcheck=False)
            self._bulletslevel = level
        if level < self._bulletslevel:
            for i in range(self._bulletslevel - level):
                self.addPart("</{0}>".format(tag), blockcheck=False)
            self._bulletslevel = level
        self.addPart("<li>%s</li>" % part, blockcheck=False)

    def _checkBlock(self, ttype, open, close):
        """
        types are : bullet,descr
        """
        # print "checkblock inblock:%s ttype:%s intype:%s" %(self._inBlock,ttype,self._inBlockType)
        if self._inBlock:
            if self._inBlockType != ttype:
                if self._inBlockType in ("bullet", "number"):
                    for i in range(self._bulletslevel):
                        self.addPart(self._inBlockClosingStatement, blockcheck=False)
                    self._bulletslevel = 0
                else:
                    self.addPart(self._inBlockClosingStatement, blockcheck=False)
                if open != "":
                    self.addPart(open, blockcheck=False)
                    self._inBlock = True
                    self._inBlockType = ttype
                    self._inBlockClosingStatement = close
                else:
                    self._inBlock = False
                    self._inBlockType = ""
                    self._inBlockClosingStatement = ""
        else:
            self.addPart(open, blockcheck=False)
            if ttype != "" and close != "":
                self._inBlock = True
                self._inBlockType = ttype
                self._inBlockClosingStatement = close
        # print "checkblock END: inblock:%s ttype:%s intype:%s" %(self._inBlock,ttype,self._inBlockType)

    # def addDescr(self, name, descr):
    #     self._checkBlock("descr", "<dl class=\"dl-horizontal\">", "</dl>")
    #     self.addPart("<dt>%s</dt>\n<dd>%s</dd>" % (name, descr), blockcheck=False)

    def addBullets(self, parts, level=1):
        """
        parts: list of bullets
        """

        # todo: figure a way for nested bullets!!
        bullets = '<ul>'
        for part in parts:
            bullets += '<li>%s</li>' % part
        bullets += '</ul>'
        self.addPart(bullets, blockcheck=False)

    def addNewLine(self, nrlines=1):
        for line in range(nrlines):
            self.addPart("", True, isElement=True)

    def addHeading(self, part, level=1):
        part = str(part)

        heading = "<h%s class=\"title\">%s</h%s>" % (level, part, level)
        self.addPart(heading, isElement=True)

    def addList(self, rows, headers="", showcolumns=[], columnAliases={}, classparams="table-condensed table-hover", linkcolumns=[]):
        """
        @param rows [[col1,col2, ...]]  (array of array of column values)
        @param headers [header1, header2, ...]
        @param linkcolumns has pos (starting 0) of columns which should be formatted as links  (in that column format needs to be $description__$link
        """
        if rows == [[]]:
            return
        if "datatables" in self.functionsAdded:
            classparams += 'cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered display dataTable'
            if headers:
                classparams += ' JSdataTable'
        if len(rows) == 0:
            return False
        l = len(rows[0])
        if str(headers) != "" and headers is not None:
            if l != len(headers):
                headers = [""] + headers
            if l != len(headers):
                print("Cannot process headers, wrong nr of cols")
                self.addPart("ERROR header wrong nr of cols:%s" % headers)
                headers = []

        c = "<table  class='table %s'>\n" % classparams  # the content
        if headers != "":
            c += "<thead><tr>\n"
            for item in headers:
                if item == "":
                    item = " "
                c = "%s<th>%s</th>\n" % (c, item)
            c += "</tr></thead>\n"
        rows3 = copy.deepcopy(rows)
        c += "<tbody>\n"
        for row in rows3:
            c += "<tr>\n"
            if row and row[0] in columnAliases:
                row[0] = columnAliases[row[0]]
            colnr = 0
            for col in row:
                if col == "":
                    col = " "
                if colnr in linkcolumns:
                    if len(col.split("__")) != 2:
                        raise RuntimeError(
                            "column which represents a link needs to be of format $descr__$link, here was:%s" %
                            col)
                    c += "<td>%s</td>\n" % self.getLink(col.split("__")[0], col.split("__")[1])
                else:
                    c += "<td>%s</td>\n" % self.getRound(col)
                colnr += 1
            c += "</tr>\n"
        c += "</tbody></table>\n\n"
        self.addPart(c, True, isElement=True)

    def addDict(self, dictobject, description="", keystoshow=[], aliases={}, roundingDigits=None):
        """
        @params aliases is dict with mapping between name in dict and name to use
        """
        if keystoshow == []:
            keystoshow = list(dictobject.keys())
        self.addPart(description)
        arr = []
        for item in keystoshow:
            if item in aliases:
                name = aliases[item]
            else:
                name = item
            arr.append([name, dictobject[item]])
        self.addList(arr)
        self.addNewLine()

    @staticmethod
    def getLink(description, link, link_id=None, link_class=None, htmlelements="", newtab=False):
        if link_id:
            link_id = ' id="%s"' % link_id.strip()
        else:
            link_id = ''

        if link_class:
            link_class = ' class="%s"' % link_class.strip()
        else:
            link_class = ''

        if newtab:
            target = 'target="_blank"'
        else:
            target = ''

        anchor = "<a href='%s' %s %s %s %s>%s</a>" % (link.strip(),
                                                      link_id.strip(),
                                                      link_class,
                                                      htmlelements,
                                                      target,
                                                      description)
        return anchor

    def addLink(self, description, link, newtab=False):
        anchor = self.getLink(description, link, newtab=newtab)
        self.addParagraph(anchor)

    def addPageBreak(self,):
        self.addPart("<hr style='page-break-after: always;'/>")

    def addComboBox(self, items):
        """
        @items is a list of tuples [ ('text to show', 'value'), ]
        """
        import random
        if items:
            id = ('dropdown%s' % random.random()).replace('.', '')
            html = '<select id=%s>\n' % (id)

            for text, value in items:
                html += '<option value="%s">%s</option>\n' % (value, text)
            html += '</select>'
            self.addHTML(html)
            return id
        else:
            return ''

    def addBootstrapCombo(self, title, items, id=None):
        self.addBootstrap()
        html = """
<div class="btn-group" ${id}>
  <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      ${title}<span class="caret"></span>
  </button>
  <ul class="dropdown-menu">
    {% for name, action in items %}
    <li><a href="javascript:void(0)" onclick="${action}">${name}</a></li>
    {% endfor %}
  </ul>
</div>
"""
        id = 'id="%s"' % id if id else ''
        html = self.jenv.from_string(html).render(items=items, title=title, id=id)
        self.addHTML(html)

    def addActionBox(self, actions):
        """
        @actions is array of array, [[$actionname1,$params1],[$actionname2,$params2]]
        """
        row = []
        for item in actions:
            action = item[0]
            actiondescr = item[1]
            if actiondescr == "":
                actiondescr = action
            params = item[2]

            if action in self.actions:
                link = self.actions[action]
                link = link.replace("{params}", params)
                row.append(self.getLink(actiondescr, link))
            else:
                raise RuntimeError("Could not find action %s" % action)
        self.addList([row])



    @staticmethod
    def _format_styles(styles):
        """
        Return CSS styles, given a list of CSS attributes
        @param styles a list of tuples, of CSS attributes, e.g. [("background-color", "green), ("border", "1px solid green")]

        >>> PageHTML._format_styles([("background-color", "green"), ("border", "1px solid green")])
        'background-color: green; border: 1px solid green'
        """
        try:
            return '; '.join('{0}: {1}'.format(*style) for style in styles)
        except IndexError:
            return ''

    def addImage(self, title, imagePath, width=None, height=None, styles=[]):
        """
        @param title alt text of the image
        @param imagePath can be url or local path
        @param width width of the image
        @param height height of the image
        @param styles a list of tuples, containing CSS attributes for the image, e.g. [("background-color", "green), ("border", "1px solid green")]
        """
        width_n_height = ''
        if width:
            width_n_height += ' width="{0}"'.format(width)
        if height:
            width_n_height += ' height="{0}"'.format(height)

        img = "<img src='%s' alt='%s' %s style='clear:both;%s' />" % (
            imagePath, title, width_n_height, PageHTML._format_styles(styles))
        self.addPart(img, isElement=True)

    def addTableWithContent(self, columnsWidth, colContents):
        """
        @param columnsWidth = Array with each element a nr, when None then HTML does the formatting, otherwise relative to each other
        @param colContents = array with each element HTML code
        """
        table = "<table><thead><tr>"
        for colWidth, colContent in zip(columnsWidth, colContents):
            if colWidth:
                table += "<th width='%s'>%s</th>" % (colWidth, colContent)
            else:
                table += "<th>%s</th>" % (colContent)
        table += "</tr></head></table>"
        self.addPart(table, isElement=True)

    def addHTML(self, htmlcode):
        #import cgi
        #html = "<pre>%s</pre>" % cgi.escape(htmlcode)
        self.addPart(htmlcode, isElement=False)

    def removeCSS(self, exclude, permanent=False):
        """
        will walk over header and remove css links
        link need to be full e.g. bootstrap.min.css
        """
        out = ""
        for line in self.head.split("\n"):
            if line.lower().find(exclude) == -1:
                out += "%s\n" % line
        self.head = out
        if permanent:
            key = exclude.strip().lower()
            self.jscsslinks[key] = True

    def addCSS(self, cssLink=None, cssContent=None, exlcude="", media=None):
        """
        """
        #TODO:*1 what is this?
        if self.pagemirror4jscss is not None:
            self.pagemirror4jscss.addCSS(cssLink, cssContent)
        if cssLink is not None:
            key = cssLink.strip().lower() + (media or '')
            if key in self.jscsslinks:
                return
            self.jscsslinks[key] = True

        mediatag = ""
        if media:
            mediatag = "media='%s'" % media
        if cssContent:
            css = "\n<style type='text/css' %s>%s\n</style>\n" % (mediatag, cssContent)
        else:
            css = "<link  href='%s' type='text/css' rel='stylesheet' %s/>\n" % (cssLink, mediatag)
        self.head += css

    def addTimeStamp(self, classname='jstimestamp'):
        js = """
        $(function() {
            var updateTime = function () {
                $(".%s").each(function() {
                    var $this = $(this);
                    var timestmp = parseFloat($this.data('ts'));
                    if (timestmp > 0)
                        var time = new Date(timestmp * 1000).toLocaleString();
                    else var time = "";
                    $this.html(time);
                });
            };
            updateTime()
            window.updateTime = updateTime;
            $(document).ajaxComplete(updateTime);
        });
        """ % classname
        if classname not in self._timestampsAdded:
            self.addJS(jsContent=js)
            self._timestampsAdded.add(classname)

    def addJS(self, jsLink=None, jsContent=None, header=True):
        if self.pagemirror4jscss is not None:
            self.pagemirror4jscss.addJS(jsLink, jsContent, header)
        if jsLink is not None:
            key = jsLink.strip().lower()
            if key in self.jscsslinks:
                return
            self.jscsslinks[key] = True

        if jsContent:
            js = "<script type='text/javascript'>\n%s</script>\n" % jsContent
        else:
            js = "<script  src='%s' type='text/javascript'></script>\n" % jsLink
            #js = "<script  src='%s' </script>\n" % jsLink
        if header:
            self.head += js
        else:
            if js not in self.tail:
                self.tail.append(js)

    def removeJS(self, jsLink=None, jsContent=None):
        out = ""
        js = ''
        if jsContent:
            js = "<script type='text/javascript'>\n%s</script>\n" % jsContent
        else:
            js = "<script  src='%s' type='text/javascript'></script>\n" % jsLink
        self.head = self.head.replace(js.strip(), '')
        self.body = self.body.replace(js.strip(), '')

    def addScriptBodyJS(self, jsContent):
        self.scriptBody = "%s%s\n" % (self.scriptBody, jsContent)

    def addJQuery(self):
        #TODO: *1 fix
        self.addJS('/jslib/jquery/jquery-2.2.1.min.js')
        self.addJS('/jslib/jquery/jquery-migrate-1.2.1.js')
        self.addJS("/jslib/jquery/jquery-ui.min.js")

    def addBootstrap3(self, jquery=True):
        
        #TODO: *1 fix

        if jquery:
            self.addJQuery()

        self.addJS('/jslib/bootstrap/js/bootstrap-3-3-6.min.js')
        self.addCSS('/jslib/bootstrap/css/bootstrap-3-3-6.min.css')

    def addBootstrap4(self, jquery=True):
        
        #TODO: *1 fix

    def addBodyAttribute(self, attribute):
        if attribute not in self.bodyattributes:
            self.bodyattributes.append(attribute)



    def addDocumentReadyJSfunction(self, function): #TODO: dont understand
        """
        e.g. $('.dataTable').dataTable();
        """
        if self.pagemirror4jscss is not None:
            self.pagemirror4jscss.addDocumentReadyJSfunction(function)
        if function not in self.documentReadyFunctions:
            self.documentReadyFunctions.append(function)

    

    def addHTMLHeader(self, header):
        self.head += header

    def addHTMLBody(self, body):
        self.body += body

    def addAccordion(self, panels):
        self.addJS('/jslib/codemirror/autorefresh.js', header=False)
        self.addPart('<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">')

        panels.sort(key=lambda x: x['title'])

        for panel_data in panels:
            if panel_data is None:
                continue

            content = panel_data['content']

            for item in ['header_id', 'section_id', 'label_id', 'label_icon', 'label_color']:
                if item not in panel_data:
                    panel_data[item] = j.data.idgenerator.generateXCharID(10)

            self.addPart("""
            <div class="panel panel-default">
              <div class="panel-heading" role="tab" id="%(header_id)s">
                <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#%(section_id)s" aria-expanded="true" aria-controls="%(section_id)s">%(title)s</a>
            """ % panel_data)

            if 'label_content' in panel_data:
                self.addPart("""
                <a id=%(label_id)s class="label-archive label label-%(label_color)s glyphicon glyphicon glyphicon-%(label_icon)s pull-right">%(label_content)s</a>
                """ % panel_data)

            self.addPart("""
                </h4>
              </div>
              <div id="%(section_id)s" class="panel-collapse collapse" role="tabpanel" aria-labelledby="%(header_id)s">
                <div class="panel-body">
                """ % panel_data)

            if panel_data.get('code', False):
                self.addCodeBlock(content, edit=False, exitpage=True, spacename='', pagename='', linenr=True, autorefresh=True)
            else:
                self.addPart(content)

            self.addPart("""
                </div> <!-- panel body-->
              </div> <!-- panel collapse-->
            </div> <!-- panel default-->""")

        self.addPart('</div>')  # close panel-group

    def getContent(self):
        return str(self)

    def __str__(self):
        # make sure we get closures where needed (/div)

        # if self.documentReadyFunctions != []:
        #     CC = "$(document).ready(function() {\n"
        #     for f in self.documentReadyFunctions:
        #         CC += "%s\n" % f
        #     CC += "} );\n"
        #     jsHead += "<script type='text/javascript'>" + CC + "</script>"
        #TODO: *1

        