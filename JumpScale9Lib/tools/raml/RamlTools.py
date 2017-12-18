
from js9 import j
import os
from .SwaggerSpec import *


class RamlTools:

    """
    server which generates & serves raml over gevent
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.raml"
        self._prefab = j.tools.prefab.local
        self.logger = j.logger.get('j.tools.raml')

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")
            
    def install(self):
        """
        """

        # self._prefab.runtimes.nodejs.reset()

        npm_install=self._prefab.runtimes.nodejs.npm_install

        if j.sal.process.checkInstalled("go") == False:
            j.tools.prefab.local.runtimes.golang.install()
            j.tools.prefab.local.runtimes.golang.goraml()
        if j.sal.process.checkInstalled("npm") == False:
            j.tools.prefab.local.runtimes.nodejs.install()
        npm_install("raml2html")
        npm_install("api-spec-converter")
        npm_install("oas-raml-converter")

        if not self._prefab.core.isMac:
            t=j.tools.code.replace_tool_get()
            t.synonymAdd(regexFind='.*node --harmony.*', replaceWith='#!/usr/bin/env node')

            t.replace_in_dir("/opt/node/bin")

        #no install appropriate pips

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

        #TODO 




    def init(self, path="", reset=False):
        """
        generate the site from path specified, if not specified will be current dir

        can call this command line too (be in path where you want to work):
        js9_raml init

        """

        if path == "":
            path = j.sal.fs.getcwd()
        else:
            j.sal.fs.createDir(path)

        if reset:
            j.sal.fs.remove("%s/api_spec" % path)
            j.sal.fs.remove("%s/generate_code.sh" % path)
            j.sal.fs.remove("%s/start_server.sh" % path)
            j.sal.fs.remove("%s/server" % path)
            j.sal.fs.remove("%s/generated" % path)
            j.sal.fs.remove("%s/htmldoc" % path)            

        if not j.sal.fs.exists("%s/api_spec" % path):
            src = "%s/baseapp/" % self._path
            j.sal.fs.copyDirTree(src, path, keepsymlinks=False,
                                 overwriteFiles=False, rsync=True, rsyncdelete=False)
            print(
                "now edit main.raml in api_spec director, and run 'js9_raml generate.")
            return

    def generate(self, path="", reset=False):
        """
        generate the site from path specified, if not specified will be current dir

        can call this command line too (be in path where you want to work): 
        js9_raml generate 
        """

        path=self._checkpath(path)

        if reset:
            j.sal.fs.remove("%s/generate_client.sh" % path)
            j.sal.fs.remove("%s/generate_server.sh" % path)
            j.sal.fs.remove("%s/server" % path)
            j.sal.fs.remove("%s/generated" % path)
            j.sal.fs.remove("%s/htmldoc" % path)
            

        def _generate():

            # goramlpath="/Users/kristofdespiegeleer1/opt/go_proj/bin/go-raml"
            rc,goramlpath,err=j.sal.process.execute("which go-raml")
            goramlpath=goramlpath.strip()

            j.sal.fs.remove("%s/generated" % path)

            cmd = "cd %s;mkdir -p generated/server;cd api_spec;%s server --language python --dir ../generated/server --ramlfile main.raml" % (path,goramlpath)
            print(cmd)
            j.sal.process.executeInteractive(cmd)

            cmd = "cd %s;mkdir -p generated/client;cd api_spec;%s client --language python --python-unmarshall-response=true --dir ../generated/client --ramlfile main.raml" % (path,goramlpath)
            print(cmd)
            j.sal.process.executeInteractive(cmd)

            cmd = "cd %s;rm -rf htmldoc;mkdir -p htmldoc;cd api_spec;raml2html -i main.raml -o ../htmldoc/api.html -v" % path
            j.sal.process.executeInteractive(cmd)

            cmd = "cd %s;cd api_spec;oas-raml-converter --from RAML --to OAS20 main.raml > ../generated/swagger_api.json" % path
            j.sal.process.execute(cmd)
        _generate()

        spec = SwaggerSpec("generated/swagger_api.json")

        j.sal.fs.createDir("%s/server" % path)

        for objname in spec.rootObjNames:
            spath = "%s/generated/server/%s_api.py" % (path, objname)
            dpath = "%s/server/%s_api.py" % (path, objname)
            # j.sal.fs.remove(dpath)  # debug
            if not j.sal.fs.exists(dpath):
                j.sal.fs.copyFile(spath, dpath)
                editor = j.tools.code.text_editor_get(dpath)
                editor.replace1Line(
                    '', ["#comment this"])

        spath = "%s/generated/server/app.py" % (path)
        dpath = "%s/server/app.py" % (path)
        if not j.sal.fs.exists(dpath):
            j.sal.fs.copyFile(spath, dpath)
            editor = j.tools.code.text_editor_get(dpath)
            editor.replace1Line('', ["#comment this"])

    
    def upgrade(self):
        self.logger.info("goraml_ugrade")
        j.tools.prefab.local.runtimes.golang.goraml(reset=True)

    def server(self,path=""):
        path=self._checkpath(path)
        cmd="sh start_server.sh"
        j.sal.process.executeInteractive(cmd)

    def _checkpath(self,path=""):
        if path == "" or path==None:
            path = j.sal.fs.getcwd()
        
        if not j.sal.fs.exists("%s/api_spec" % path):
            raise RuntimeError("Cannot find api_spec dir in %s, please use 'js9_raml init' to generate."%path)

        return path