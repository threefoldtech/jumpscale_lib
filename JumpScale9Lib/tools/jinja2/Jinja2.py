from js9 import j

from jinja2 import Template

JSBASE = j.application.jsbase_get_class()

class Jinja2(JSBASE):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.jinja2"
        JSBASE.__init__(self)
        self.reset()
        self.logger_enable()


    def reset(self):
        self.templates = {}
        

    def template_get(self,path,key=""):
        """
        returns template and will be cached
        if key used then will use key as the key in the caching
        """
        if key is  "":
            key = path
        if key not in self.templates:
            C = j.sal.fs.readFile(path)
            self.templates[key] = Template(C)

        return self.templates[key]

    def template_render(self,path,**args):
        if j.sal.fs.getBaseName(path).startswith("_") or "__py" in path:
            return
        self.logger.debug("template render:%s"%path)
        # print(path)
        C = j.sal.fs.readFile(path)
        t = Template(C)
        return t.render(**args)

    def text_render(self,text,**args):
        """
        render text

        std arguments given to renderer:

        - DIRS - j.dirs

        j.tools.jinja2.text_render("{{DIRS.TMPDIR}}")

        """

        t = Template(text)
        return t.render(DIRS=j.dirs,**args)


    def file_render(self,path,**args):
        """
        will read file, render & then overwrite the same file

        std arguments given to renderer:

        - DIRS - j.dirs

        """
        if j.sal.fs.getBaseName(path).startswith("_"):
            return
        C = self.template_render(path, DIRS=j.dirs, **args)
        if C is not None:
            j.sal.fs.writeFile(path,C)

    def dir_render(self,path, recursive=True, filter=None, minmtime=None, maxmtime=None, depth=None,\
             exclude=[], followSymlinks=False, listSymlinks=False,**args):

        for item in  j.sal.fs.listFilesInDir(path=path,recursive=recursive,filter=filter,\
                minmtime=minmtime,maxmtime=maxmtime,depth=depth,exclude=exclude,followSymlinks=followSymlinks,listSymlinks=listSymlinks):
            self.file_render(item,**args)

    def copy_dir_render(self,src,dest,overwriteFiles=False,filter=None, ignoredir=[],ignorefiles=[],reset=False,**args):
        """
        copy dir from src to dest
        use ignoredir & ignorefiles while copying
        filter is used where templates are applied on (will copy more in other words)

        example:

        src = j.clients.git.getContentPathFromURLorPath("https://github.com/rivine/recordchain/tree/development/apps/example")
        dest = j.sal.fs.getTmpDirPath("jumpscale/jinja2test")
        self.logger.info("copy templates to:%s"%dest)
        j.tools.jinja2.copy_dir_render(src,dest,j=j,name="aname")

        """
        if ignoredir==[]:
            ignoredir=['.egg-info', '.dist-info']
        if ignorefiles == []:
            ignorefiles=['.egg-info','.pyc','.bak']

        if reset:
            j.sal.fs.removeDirTree(dest)

        j.sal.fs.createDir(dest)
                        
        j.sal.fs.copyDirTree(src, dest, keepsymlinks=False, overwriteFiles=overwriteFiles, ignoredir=ignoredir, \
            ignorefiles=ignorefiles, rsync=True, recursive=True, rsyncdelete=True, createdir=False)

        self.dir_render(path=dest,filter=filter,**args)

    def test(self):
        """
        js9 'j.tools.jinja2.test()'
        """

        src = j.clients.git.getContentPathFromURLorPath("https://github.com/rivine/recordchain/tree/development/apps/example")
        dest = j.sal.fs.getTmpDirPath("jumpscale/jinja2test")
        self.logger.info("copy templates to:%s"%dest)
        j.tools.jinja2.copy_dir_render(src,dest,j=j,name="aname")