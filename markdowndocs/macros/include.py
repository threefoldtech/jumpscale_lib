
def include(doc, name, **args):
    name = name.lower()
    
    if name.find(":") == -1:
        doc = doc.docsite.doc_get(name, die=False)
        if doc != None:
            doc.process()
            newcontent = doc.content
        else:
            newcontent = "ERROR: COULD NOT INCLUDE:%s (not found)" % name

    else:
        docsiteName, name = name.split(":")
        docsite = j.tools.docgenerator.docsite_get(docsiteName)
        doc = docsite.doc_get(name, die=False)
        if doc != None:
            doc.process()
            newcontent = doc.content
        else:
            newcontent = "ERROR: COULD NOT INCLUDE:%s:%s (not found)" % (docsiteName, name)

    # if name in self._contentPaths:
    #     newcontent0 = j.sal.fs.fileGetContents(self._contentPaths[name])
    #
    #     newcontent = ""
    #
    #     pre = "#" * self.last_level
    #
    #     for line in newcontent0.split("\n"):
    #         if line.find("#") != -1:
    #             line = pre + line
    #         newcontent += "%s\n" % line

    return newcontent
