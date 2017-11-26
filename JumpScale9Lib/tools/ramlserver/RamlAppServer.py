
from js9 import j
import os
from .SwaggerSpec import *


class RamlAppServer:

    """
    server which generates & serves raml over gevent
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.ramlAppServer"

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def _nodeInstall(self, cmdname, name, reset=False):
        if reset or j.sal.process.checkInstalled(cmdname) == False:
            print("nodeinstall:%s" % cmdname)
            npath = j.sal.fs.joinPaths(j.dirs.VARDIR, "nodejs_modules")
            if not j.sal.fs.exists(npath):
                j.sal.fs.createDir(npath)
            cmd = "cd %s;npm i %s" % (npath, name)
            j.sal.process.executeInteractive(cmd)

            srcCmd = "%s/templates/%s" % (self._path, name)
            cmdpath = "%s/nodejs_modules/node_modules/%s/bin/%s" % (
                j.dirs.VARDIR, name, name)

            if j.sal.fs.exists(srcCmd):
                j.sal.fs.chmod(srcCmd, 0o770)
                j.sal.fs.symlink(srcCmd, "/usr/local/bin/%s" %
                                 name, overwriteTarget=True)
                j.sal.fs.chmod(cmdpath, 0o770)

            if j.sal.fs.exists(cmdpath):
                j.sal.fs.symlink(cmdpath, "/usr/local/bin/%s" %
                                 name, overwriteTarget=True)
            return "%s/nodejs_modules/node_modules/%s" % (j.dirs.VARDIR, name)
        else:
            return None

    def _checkEnv(self):
        """
        """

        if j.sal.process.checkInstalled("go") == False:
            j.tools.prefab.local.runtimes.golang.install()
        if j.sal.process.checkInstalled("npm") == False:
            j.tools.prefab.local.runtimes.nodejs.install()
        self._nodeInstall("raml2html", "raml2html")
        self._nodeInstall("api-spec-converter", "api-spec-converter")

        # next no longer needed
        # self._nodeInstall("api-spec-transformer",
        #                   "api-spec-transformer", reset=True)

        res = self._nodeInstall("raml_converter", "oas-raml-converter")
        if res is not None:
            j.sal.fs.symlink("%s/lib/bin/converter.js" % res,
                             "/usr/local/bin/raml_converter", overwriteTarget=True)

        if j.sal.process.checkInstalled("go-raml") == False:
            grpath = j.sal.fs.joinPaths(j.dirs.HOMEDIR, "go", "bin", "go-raml")
            if not j.sal.fs.exists(grpath):
                j.sal.process.execute("go get -u github.com/Jumpscale/go-raml")
            if j.sal.fs.exists(grpath):
                j.sal.fs.symlink(
                    grpath, "/usr/local/bin/go-raml", overwriteTarget=True)
            else:
                raise RuntimeError(
                    "could not find go-raml on right spot: '%s', was it generated" % grpath)

    def generate(self, path="", reset=False):
        """
        generate the site from path specified, if not specified will be current dir
        """
        self._checkEnv()
        if path == "":
            path = j.sal.fs.getcwd()

        if reset:
            j.sal.fs.remove("%s/api_spec" % path)
            j.sal.fs.remove("%s/generate_client.sh" % path)
            j.sal.fs.remove("%s/generate_server.sh" % path)
            j.sal.fs.remove("%s/server" % path)

        if not j.sal.fs.exists("%s/api_spec" % path):
            src = "%s/baseapp/" % self._path
            j.sal.fs.copyDirTree(src, path, keepsymlinks=False,
                                 overwriteFiles=False, rsync=True, rsyncdelete=False)
            print(
                "now edit main.raml in api_spec director, and re-run this command when done.")
            return

        def _generate():

            j.sal.fs.remove("%s/generated"%path)

            cmd = "cd %s;mkdir -p generated/server;cd api_spec;go-raml server --language python --dir ../generated/server --ramlfile main.raml" % path
            j.sal.process.executeInteractive(cmd)

            cmd = "cd %s;mkdir -p generated/client;cd api_spec;go-raml client --language python --python-unmarshall-response=true --dir ../generated/client --ramlfile main.raml" % path
            j.sal.process.executeInteractive(cmd)

            cmd = "cd %s;rm -rf htmldoc;mkdir -p htmldoc;cd api_spec;raml2html -i main.raml -o ../htmldoc/api.html -v" % path
            j.sal.process.executeInteractive(cmd)

            cmd = "cd %s;cd api_spec;raml_converter --from RAML --to OAS20 main.raml > ../generated/swagger_api.json" % path
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
                editor = j.tools.code.textEditorGet(dpath)
                editor.replace1Line('', ["comment this when in js9 ramlserver"])

        spath = "%s/generated/server/app.py" % (path)
        dpath = "%s/server/app.py" % (path)
        if not j.sal.fs.exists(dpath):
            j.sal.fs.copyFile(spath, dpath)
            editor = j.tools.code.textEditorGet(dpath)
            editor.replace1Line('', ["comment this when in js9 ramlserver"])

