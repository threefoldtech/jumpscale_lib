from Jumpscale import j
import os
from jinja2 import Template
import imp

JSBASE = j.application.JSBaseClass

class Jinja2(JSBASE):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.jinja2"
        JSBASE.__init__(self)
        self.reset()
        self.logger_enable()
        j.sal.fs.createDir("%s/CODEGEN"%j.dirs.VARDIR)
        self.reset(destroyall=False)


    def reset(self,destroyall=True):
        """
        js_shell 'j.tools.jinja2.reset()'

        :param destroyall: all templates will be removed from disk
        :return:
        """
        self._path_to_contenthash = {} #path remembers what the hash of content is
        self._hash_to_template = {}
        self._hash_to_codeobj = {}
        if destroyall:
            j.sal.fs.remove("%s/CODEGEN"%j.dirs.VARDIR)
        j.sal.fs.createDir("%s/CODEGEN"%j.dirs.VARDIR)
        

    def template_get(self,path="",text="",reload=False):
        """
        returns jinja2 template and will be cached
        if key used then will use key as the key in the caching
        """
        md5=""
        if path!="":
            if reload==False and path in self._path_to_contenthash:
                md5 = self._path_to_contenthash[path]
            if md5 =="" or not md5 in self._hash_to_template:
                text = j.sal.fs.readFile(path)
                md5=""

        if md5 == "":
            md5 = j.data.hash.md5_string(text)

        if md5 not in self._hash_to_template:
            # if text=="":
            #     self.logger.info("create template:%s"%path)
            # else:
            #     self.logger.info("create template:\n%s"%text)
            self._hash_to_template[md5] = Template(text)
            self._hash_to_template[md5].md5 = md5

        return self._hash_to_template[md5]

    def template_render(self,path="",text="",dest="",reload=False, **args):
        """
        load the template, do not write back
        render & return result as string
        """
        # self.logger.debug("template render:%s"%path)
        t = self.template_get(path=path,text=text,reload=reload)
        return t.render(**args)

    def code_python_render(self, obj_key, path="",text="",dest="",reload=False, objForHash=None, **args):
        """

        :param obj_key:  is name of function or class we need to evaluate when the code get's loaded
        :param path: path of the template (is path or text to be used)
        :param text: if not path used, text = is the text of the template (the content)
        :param dest: if not specified will be in j.dirs.VARDIR,"CODEGEN",md5+".py" (md5 is md5 of template+msgpack of args)
        :param reload: will reload the template and re-render
        :param args: arguments for the template (DIRS will be passed by default)
        :return:
        """
        t = self.template_get(path=path,text=text,reload=reload)
        if "j" in args:
            args.pop("j")
        if objForHash:
            tohash=j.data.serializers.msgpack.dumps(objForHash)+t.md5.encode()+obj_key.encode()
        else:
            tohash=j.data.serializers.msgpack.dumps(args)+t.md5.encode()+obj_key.encode() #make sure we have unique identifier
        md5=j.data.hash.md5_string(tohash)
        if md5 not in self._hash_to_codeobj:
            #means the code block is not there yet
            # print("code not htere yet")
            if dest == "":
                dest = j.sal.fs.joinPaths(j.dirs.VARDIR,"CODEGEN",md5+".py")
            if not j.sal.fs.exists(dest):
                #means has not been rendered yet lets do
                out = t.render(j=j,DIRS=j.dirs,**args)
                j.sal.fs.writeFile(dest,out)
            try:
                m=imp.load_source(name=md5, pathname=dest)
            except Exception as e:
                msg = "COULD not load source:%s\n"%dest
                if path!="":
                    msg += "path from original template:%s\n"%path
                else:
                    msg+="original template:\n\n%s"%text
                msg+="TO LOAD SCRIPT CONTENT:\n%s\n\n"%out
                raise RuntimeError(msg)
            try:
                obj = eval("m.%s"%obj_key)
            except Exception as e:
                msg = "COULD not import source:%s\n"%dest
                msg += "obj_key:%s\n"%obj_key
                if path!="":
                    msg += "path from original template:%s\n"%path
                else:
                    msg+="original template:\n\n%s"%text
                msg+="TO LOAD SCRIPT CONTENT:\n%s\n\n"%out
                raise RuntimeError(msg)
            self._hash_to_codeobj[md5]=obj
        return self._hash_to_codeobj[md5]



    def file_render(self,path,write=True,dest=None,**args):
        """
        will read file, render & then overwrite the same file

        std arguments given to renderer:

        - DIRS - j.dirs
        
        if dest is noe then the source file will be overwritten

        """
        if j.sal.fs.getBaseName(path).startswith("_") or "__py" in path:
            if "__init__" not in path:
                raise RuntimeError("cannot render path:%s"%path)
        C = self.template_render(path=path, DIRS=j.dirs, **args)
        if C is not None and write:
            if dest:
                path=dest
            j.sal.fs.writeFile(path,C)
        return C

    def dir_render(self,path, recursive=True, filter=None, minmtime=None, maxmtime=None, depth=None,\
             exclude=[], followSymlinks=False, listSymlinks=False,**args):
        
        if exclude == []:
            exclude=['*.egg-info','*.pyc','*.bak','*__pycache__*']
    
        for item in  j.sal.fs.listFilesInDir(path=path,recursive=recursive,filter=filter,\
                minmtime=minmtime,maxmtime=maxmtime,depth=depth,exclude=exclude,followSymlinks=followSymlinks,listSymlinks=listSymlinks):
            if j.sal.fs.getBaseName(path).startswith("_") or "__py" in path:
                continue                
            self.file_render(item,**args)

    def copy_dir_render(self,src,dest,overwriteFiles=False,filter=None, ignoredir=[],ignorefiles=[],reset=False,render=True,**args):
        """
        copy dir from src to dest
        use ignoredir & ignorefiles while copying
        filter is used where templates are applied on (will copy more in other words)

        example:

        src = j.clients.git.getContentPathFromURLorPath("https://github.com/threefoldtech/jumpscale_lib/tree/development/apps/example")
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

        if render:
            self.dir_render(path=dest,filter=filter,**args)

    def test(self):
        """
        js_shell 'j.tools.jinja2.test()'
        """

        src = j.clients.git.getContentPathFromURLorPath("https://github.com/threefoldtech/jumpscale_lib/tree/development/apps/example")
        dest = j.sal.fs.getTmpDirPath("jumpscale/jinja2test")
        self.logger.info("copy templates to:%s"%dest)
        j.tools.jinja2.copy_dir_render(src,dest,j=j,name="aname")

        self.test_performance()

    def test_performance(self):
        """
        js_shell 'j.tools.jinja2.test_performance()'
        """
        path = j.sal.fs.getDirName(os.path.abspath(__file__))+"/test_class.py"
        j.tools.timer.start("jinja_code")
        nr=1000
        obj=self.code_python_render(obj_key="MyClass", path=path,reload=True, name="name:%s"%1)
        for x in range(nr):
            obj=self.code_python_render(obj_key="MyClass", path=path,reload=False, name="name:%s"%x)
        res= j.tools.timer.stop(nr)
        assert res > 500

        j.tools.timer.start("jinja_code2") #here we open class which has already been rendered
        nr=1000
        for x in range(nr):
            obj=self.code_python_render(obj_key="MyClass", path=path,reload=False, name="name:%s"%1) #now use same
        res= j.tools.timer.stop(nr)
        assert res > 5000

        C="""
        somedata = {{name}}
        somethingelse= {{j.data.time.epoch}}
        """

        j.tools.timer.start("jinja")
        nr=5000
        for x in range(nr):
            R=self.template_render(text=C,reload=False, j=j,name="myname:%s"%x)
        res= j.tools.timer.stop(nr)
        assert res > 10000

        self.reset()





