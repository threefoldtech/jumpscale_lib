
def dot(doc, name, content):

    md5 = j.data.hash.md5_string(content)
    md5 = bytes(md5.encode())
    md5b = j.core.db.get("docgenerator:dot:%s" % name)

    if md5b != md5:
        path = j.sal.fs.getTmpFilePath()
        j.sal.fs.writeFile(filename=path, contents=content)
        dest = j.sal.fs.joinPaths(j.sal.fs.getDirName(doc.path), "%s.png" % name)
        j.sal.process.execute("dot '%s' -Tpng > '%s'" % (path, dest))
        j.sal.fs.remove(path)
        doc.docsite.addFile(dest)
        j.core.db.set("docgenerator:dot:%s" % name, md5)

    return "![%s.png](../../files/%s.png)" % (name, name)
