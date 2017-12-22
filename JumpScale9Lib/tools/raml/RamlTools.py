
from js9 import j
import os
from .SwaggerSpec import *


class RamlToolsFactory:

    """
    server which generates & serves raml over gevent
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.raml"
        self._prefab = j.tools.prefab.local
        self.logger = j.logger.get('j.tools.raml')

    def _check(self):
        rc,self._goramlpath,err = j.sal.process.execute("which go-raml")
        if rc>0:
            raise RuntimeError("Cannot find go-raml, please call 'js9_raml install'")
        self._goramlpath = self._goramlpath.strip()        

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")
            
    def install(self,serverpips=False):
        """
        """

        self.logger.info("goraml_install")

        # self._prefab.runtimes.nodejs.reset()
        npm_install=self._prefab.runtimes.nodejs.npm_install

        if j.sal.process.checkInstalled("go") == False:
            j.tools.prefab.local.runtimes.golang.install()
            j.tools.prefab.local.runtimes.golang.goraml(reset=True)
        if j.sal.process.checkInstalled("npm") == False:
            j.tools.prefab.local.runtimes.nodejs.install()

        npm_install("raml2html")
        npm_install("api-spec-converter")
        npm_install("oas-raml-converter")

        if not self._prefab.core.isMac:
            t=j.tools.code.replace_tool_get()
            t.synonymAdd(regexFind='.*node --harmony.*', replaceWith='#!/usr/bin/env node')
            t.replace_in_dir("/opt/node/bin")

        j.tools.prefab.local.system.package.install("capnp")

        #now install appropriate pips
        j.tools.prefab.local.runtimes.pip.install("autopep8")

        if serverpips:
            pips='''
            Flask==0.10.1
            Flask-Inputs==0.2.0
            Jinja2==2.8
            MarkupSafe==0.23
            Werkzeug==0.11.4
            itsdangerous==0.24
            jsonschema==2.5.1
            six==1.10.0
            python-jose==1.3.2
            '''
            j.tools.prefab.local.runtimes.pip.install(pips)


    def upgrade(self):
        self.logger.info("goraml_ugrade")
        j.tools.prefab.local.runtimes.golang.goraml(reset=True)

    def get(self,path="",init=False):
        """
        if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml init ...

        @PARAM init, if True will remove all existing directories, so be careful !

        """
        self._check()
        if path == "":
            path = j.sal.fs.getcwd()
        else:
            j.sal.fs.createDir(path)
        if init:
            self._remove(path)
            src = "%s/baseapp/" % self._path
            j.sal.fs.copyDirTree(src, path, keepsymlinks=False,
                                overwriteFiles=False, rsync=True, rsyncdelete=False)
            print("now edit main.raml in api_spec director, and run 'js9_raml generate_pyserver or other")
            return RamlTools(path)

        return RamlTools(path)

    def _remove(self,path,all=True):
        j.sal.fs.remove("%s/server" % path)
        j.sal.fs.remove("%s/generated" % path)
        j.sal.fs.remove("%s/htmldoc" % path)  
        j.sal.fs.remove("%s/generate_client.sh" % path)
        j.sal.fs.remove("%s/generate_server.sh" % path)
        if all:
            j.sal.fs.remove("%s/api_spec" % path)
        j.sal.fs.remove("%s/generate_code.sh" % path)
        j.sal.fs.remove("%s/start_server.sh" % path)
    

    def test(self):
        self.install(True)
        path="/tmp/ramltest"
        c=self.get(path=path,init=True)
        c.specs_get("https://github.com/itsyouonline/identityserver/tree/master/specifications/api")
        # c.client_python_generate()
        c.reset()

        jwt=j.clients.itsyouonline.jwt

        c.client_python_generate()
        #TODO:*1 call some methods on IYO server by means of the jwt

        #TODO:*1 get SPORE client, and do test from SPORE client

        c.server_python_generate()
        #TODO:*1 now start the server (purely from generated in tmux)
        #TODO:*1 use client to connect to server, do some action on the api

        c.server_python_generate(gevent=False)
        #TODO:*1 now start the server (purely from generated in tmux)
        #TODO:*1 use client to connect to server, do some action on the api

        #TODO: *1 tarantool & golang (server only)

        raise RuntimeError("need to implement all todo's")
        


class RamlTools():

    def __init__(self, path):
        self.path=path
        if not j.sal.fs.exists("%s/api_spec" % self.path):
            raise RuntimeError("Cannot find api_spec dir in %s, please use 'js9_raml init' to generate."%path)


    def _prepare(self,reset=False):
        if reset:
            self.reset()
        else:
            j.sal.fs.remove("%s/generated" % self.path)
            j.sal.fs.remove("%s/htmldoc" % self.path)     

    def reset(self):
        j.tools.raml._remove(self.path,all=False) 

    def specs_get(self,giturl):
        """
        e.g. https://github.com/itsyouonline/identityserver/tree/master/specifications/api
        """
        specpath_downloaded=j.clients.git.getContentPathFromURLorPath(giturl)
        specpath="%s/api_spec" % self.path
        j.sal.fs.remove(specpath)
        j.sal.fs.copyDirTree(specpath_downloaded,specpath)
        sfiles=j.sal.fs.listFilesInDir(specpath)
        sfile="%s/main.raml"%specpath        
        if len(sfiles)==1:
            #check is main.raml, if not rename
            sfile="%s/main.raml"%specpath
            if not j.sal.fs.exists(sfile):
                print("could not find main raml, file will rename")
                j.sal.fs.renameFile(sfiles[0],sfile)
        else:
            if not j.sal.fs.exists(sfile):
                raise RuntimeError("could not find specfile:%s"%sfile)

    def client_python_generate(self,reset=False):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml client_generate 
        """
        self._prepare(reset=reset)
        goramlpath=j.tools.raml._goramlpath

        cmd = "cd %s;mkdir -p generated/client;cd api_spec;%s client --language python --python-unmarshall-response=true --dir ../generated/client --ramlfile main.raml" %  (self.path,goramlpath)
        print(cmd)
        j.sal.process.executeInteractive(cmd)

        cmd = "cd %s;rm -rf htmldoc;mkdir -p htmldoc;cd api_spec;raml2html -i main.raml -o ../htmldoc/api.html -v" % self.path
        j.sal.process.executeInteractive(cmd)

        cmd = "cd %s;cd api_spec;oas-raml-converter --from RAML --to OAS20 main.raml > ../generated/swagger_api.json" % self.path
        j.sal.process.execute(cmd)

    def server_python_generate(self,reset=False,gevent=True):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work): 
        js9_raml generate 
        """

        self._prepare(reset=reset)
        goramlpath=j.tools.raml._goramlpath

        if gevent:
            gevent="--kind gevent-flask "
        else:
            gevent=""

        cmd = "cd %s;mkdir -p generated/server;cd api_spec;%s server --language python  %s--dir ../generated/server --ramlfile main.raml" % (self.path,goramlpath,gevent)
        print(cmd)
        j.sal.process.execute(cmd)

        cmd = "cd %s;mkdir -p generated/client;cd api_spec;%s client --language python --python-unmarshall-response=true --dir ../generated/client --ramlfile main.raml" % (self.path,goramlpath)
        print(cmd)
        j.sal.process.execute(cmd)

        cmd = "cd %s;rm -rf htmldoc;mkdir -p htmldoc;cd api_spec;raml2html -i main.raml -o ../htmldoc/api.html -v" % self.path
        j.sal.process.execute(cmd)

        cmd = "cd %s;cd api_spec;oas-raml-converter --from RAML --to OAS20 main.raml > ../generated/swagger_api.json" % self.path
        j.sal.process.execute(cmd)

        spec = SwaggerSpec("%s/generated/swagger_api.json"%self.path)

        j.sal.fs.createDir("%s/server" % self.path)

        for objname in spec.rootObjNames:
            spath = "%s/generated/server/%s_api.py" %  (self.path, objname)
            dpath = "%s/server/%s_api.py" %  (self.path, objname)
            # j.sal.fs.remove(dpath)  # debug
            if not j.sal.fs.exists(dpath):
                j.sal.fs.copyFile(spath, dpath)

                #THIS WAS NEEDED TO GET IT TO WORK IN THIS CONFIG
                # editor = j.tools.code.text_editor_get(dpath)
                # editor.replace1Line(
                #     '', ["#comment this"])

        spath = "%s/generated/server/app.py" %  (self.path)
        dpath = "%s/server/app.py" %  (self.path)
        if not j.sal.fs.exists(dpath):
            j.sal.fs.copyFile(spath, dpath)

            #THIS WAS NEEDED TO GET IT TO WORK IN THIS CONFIG
            # editor = j.tools.code.text_editor_get(dpath)
            # editor.replace1Line('', ["#comment this"])

    def server(self):
        cmd="cd %s;sh start_server.sh"%self.path
        j.sal.process.executeInteractive(cmd)

