
import os
import sys

from js9 import j

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
        rc, self._goramlpath, err = j.sal.process.execute("which go-raml")
        if rc > 0:
            raise RuntimeError("Cannot find go-raml, please call 'js9_raml install'")
        self._goramlpath = self._goramlpath.strip()

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def install(self, serverpips=False):
        """
        """

        self.logger.info("goraml_install")

        # self._prefab.runtimes.nodejs.reset()
        npm_install = self._prefab.runtimes.nodejs.npm_install

        if j.sal.process.checkInstalled("go") == False:
            j.tools.prefab.local.runtimes.golang.install()
            j.tools.prefab.local.runtimes.golang.goraml(reset=True)
        if j.sal.process.checkInstalled("npm") == False:
            j.tools.prefab.local.runtimes.nodejs.install()

        npm_install("raml2html")
        npm_install("api-spec-converter")
        npm_install("oas-raml-converter")

        if not self._prefab.core.isMac:
            t = j.tools.code.replace_tool_get()
            t.synonymAdd(regexFind='.*node --harmony.*', replaceWith='#!/usr/bin/env node')
            t.replace_in_dir("/opt/node/bin")

        if not self._prefab.core.isMac:
            j.tools.prefab.local.system.package.install("capnproto")
        else:
            j.tools.prefab.local.system.package.install("capnp")

        # now install appropriate pips
        j.tools.prefab.local.runtimes.pip.install("autopep8")

        if serverpips:
            pips = '''
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

    def get(self, path="", init=False):
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

    def _remove(self, path, all=True):
        j.sal.fs.remove("%s/server" % path)
        j.sal.fs.remove("%s/generated" % path)
        j.sal.fs.remove("%s/generate_client.sh" % path)
        j.sal.fs.remove("%s/generate_server.sh" % path)
        if all:
            j.sal.fs.remove("%s/api_spec" % path)
        j.sal.fs.remove("%s/generate_code.sh" % path)
        j.sal.fs.remove("%s/start_server.sh" % path)

    def test(self):
        self.install(True)
        path = '/tmp/ramltest'
        c = self.get(path=path, init=True)
        c.reset()

        # jwt = j.clients.itsyouonline.jwt
        # username = j.tools.configmanager.config.data['login_name']

        try:
            # Test Flask Server
            self.logger.info('generate python server')
            c.server_python_generate(kind='flask')
            tmux = j.tools.prefab.local.system.processmanager.get('tmux')
            cmd = 'cd %s/server; python3 app.py' % path
            tmux.ensure('ramltest_python_server', cmd)

            self.logger.info('generate python requests client')
            # load generated client
            c.client_python_generate(kind='requests', unmarshall_response=False)  # if unmarshal is true, the client will
            # fail because the server return empty payload

            sys.path.append('/tmp/ramltest/generated')

            self.logger.info('test generated client')
            from client import Client
            cl = Client()
            cl.api.base_url = 'http://localhost:5000'

            self.logger.info('test generate python server with generated python client')

            cl.api.user.getUser(id='1')
            tmux.stop('ramltest_python_server')

            j.sal.process.killProcessByPort(5000)  # For some reason after stopping the tmux, there is an orphan process
            # running on 5000

            # Test Gevent Server
            self.logger.info("generate python gevent server")
            c.server_python_generate(kind='gevent')
            cmd = 'cd %s/server; python3 server.py' % path
            tmux.ensure('ramltest_gevent_server', cmd)

            self.logger.info('generate python gevent client')
            # load generated client
            c.client_python_generate(kind='gevent', unmarshall_response=False)  # if unmarshall is true, the client will
            # fail because the server return empty payload

            self.logger.info('test generated client')
            from client import Client
            cl = Client()
            cl.api.base_url = 'http://localhost:5000'

            self.logger.info('test generate python server with generated python client')

            r=cl.api.user.getUser(id='1')
            assert r.json() == {}
            assert r.status_code==200

            #TODO:*1 should test the api docs: http://localhost:5000/apidocs/index.html?raml=api.raml, just to see they are there

            tmux.stop('ramltest_gevent_server')

            # TODO:*1 get SPORE client, and do test from SPORE client

            # TODO: fix support for golang
            # doesn't work now cause go code needs to be in GOPATH
            # to build

            # self.logger.info("generate golang server")
            # c.server_go_generate()
            # cmd = 'cd %s/server; go run main.go' % path
            # tmux.ensure('ramltest_golang_server', cmd)
            # self.logger.info("test generate golang server with generated python client")
            # cl.api.users.ListAPIKeys(username)
            # tmux.stop('ramltest_golang_server')

            # self.logger.info("generate lua server")
            # c.server_go_generate()
            # tmux.ensure('ramltest_golang_server', cmd)
            # self.logger.info("test generate lua server with generated python client")
            # cl.api.users.ListAPIKeys(username)
            # tmux.stop('ramltest_golang_server')

        finally:
            sys.path.remove('/tmp/ramltest/generated')

        # raise RuntimeError("need to implement all todo's")


class RamlTools:

    def __init__(self, path):
        self.path = path
        self.goramlpath = j.tools.raml._goramlpath
        if not j.sal.fs.exists("%s/api_spec" % self.path):
            raise RuntimeError("Cannot find api_spec dir in %s, please use 'js9_raml init' to generate." % path)

    def _prepare(self, reset=False):
        if reset:
            self.reset()
        else:
            j.sal.fs.remove("%s/generated" % self.path)

    def _get_kind(self, supported_kinds, kind):
        try:
            kind = supported_kinds[kind]
        except KeyError:
            raise ValueError("Kind of server/client not supported : %s" % kind)
        return kind

    def reset(self):
        j.tools.raml._remove(self.path, all=False)

    @property
    def generated_path(self):
        return j.sal.fs.joinPaths(self.path, 'generated')

    def specs_get(self, giturl):
        """
        e.g. https://github.com/itsyouonline/identityserver/tree/master/specifications/api
        """
        specpath_downloaded = j.clients.git.getContentPathFromURLorPath(giturl)
        specpath = "%s/api_spec" % self.path
        j.sal.fs.remove(specpath)
        j.sal.fs.copyDirTree(specpath_downloaded, specpath)
        sfiles = j.sal.fs.listFilesInDir(specpath)
        sfile = "%s/main.raml" % specpath
        if len(sfiles) == 1:
            # check is main.raml, if not rename
            sfile = "%s/main.raml" % specpath
            if not j.sal.fs.exists(sfile):
                print("could not find main raml, file will rename")
                j.sal.fs.renameFile(sfiles[0], sfile)
        else:
            if not j.sal.fs.exists(sfile):
                raise RuntimeError("could not find specfile:%s" % sfile)

    def _get_cmd(self, no_apidocs=False, no_main=False, lib_root_urls='', import_path='', api_file_per_method=False,
                    kind='', package='', unmarshall_response=False):
        cmd = "cd {path};mkdir -p generated/client;cd api_spec;{goraml} {type} --language {lang} \
                    --dir ../generated/{type}/ --ramlfile main.raml"
        if no_apidocs:
            cmd += ' --no-apidocs'
        if no_main:
            cmd += ' --no-main'
        if lib_root_urls:
            cmd += ' --lib-root-urls {urls}'
        if import_path:
            cmd += ' --import-path {import_path}'
        if api_file_per_method:
            cmd += ' --api-file-per-method'
        if package:
            cmd += ' --package {package}'
        if kind:
            cmd += ' --kind {kind}'
        if unmarshall_response:
            cmd += ' --python-unmarshall-response'

        return cmd

    def _client_generate(self, reset=False, cmd='', doc=True):
        self._prepare(reset=reset)

        j.sal.process.executeInteractive(cmd)
        j.sal.fs.createEmptyFile(j.sal.fs.joinPaths(self.generated_path, '__init__.py'))

        if doc:
            cmd = "cd %s;rm -rf htmldoc;mkdir -p htmldoc; \
            cd ../api_spec;raml2html -i main.raml -o ../generated/htmldoc/api.html -v" % self.generated_path
            j.sal.process.executeInteractive(cmd)

        # TODO: test and re-enable
        # cmd = "cd %s;cd api_spec;oas-raml-converter --from RAML --to OAS20 main.raml > ../generated/swagger_api.json" % self.path
        # j.sal.process.execute(cmd)

    def _server_generate(self, reset=False, cmd=''):

        self._prepare(reset=reset)
        j.sal.process.execute(cmd)

        # self._client_generate(lang=lang, kind=kind, reset=False)

        # TODO: re-enable when generation of swagger is fixed
        # spec = SwaggerSpec("%s/generated/swagger_api.json" % self.path)

        # if lang == 'python':
        #     j.sal.fs.createDir("%s/server" % self.path)
        #
        #     for objname in spec.rootObjNames:
        #         spath = "%s/generated/server/%s_api.py" % (self.path, objname)
        #         dpath = "%s/server/%s_api.py" % (self.path, objname)
        #         # j.sal.fs.remove(dpath)  # debug
        #         if not j.sal.fs.exists(dpath):
        #             j.sal.fs.copyFile(spath, dpath)
        #
        #             # THIS WAS NEEDED TO GET IT TO WORK IN THIS CONFIG
        #             # editor = j.tools.code.text_editor_get(dpath)
        #             # editor.replace1Line(
        #             #     '', ["#comment this"])
        #
        #     spath = "%s/generated/server/app.py" % (self.path)
        #     dpath = "%s/server/app.py" % (self.path)
        #     if not j.sal.fs.exists(dpath):
        #         j.sal.fs.copyFile(spath, dpath)
        #
        #         # THIS WAS NEEDED TO GET IT TO WORK IN THIS CONFIG
        #         # editor = j.tools.code.text_editor_get(dpath)
        #         # editor.replace1Line('', ["#comment this"])

        spath = '%s/generated/server/' % self.path
        dpath = '%s/server/' % self.path

        files = j.sal.fs.listFilesInDir(spath, recursive=True)

        for file in files:
            relative_file = file.replace(spath, '')
            destination_file = j.sal.fs.joinPaths(dpath, relative_file)
            if not j.sal.fs.exists(destination_file):
                j.sal.fs.copyFile(file, destination_file, createDirIfNeeded=True)

    def client_python_generate(self, reset=False, kind='requests', unmarshall_response=True, doc=True):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml generate_pyclient
        """
        supported_map = {
                'gevent': 'gevent-requests',
                'requests': 'requests',
                'aiohttp': 'aiohttp',
        }
        kind = self._get_kind(supported_map, kind)

        cmd = self._get_cmd(kind=kind, unmarshall_response=unmarshall_response)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, kind=kind, lang='python', type='client')

        self._client_generate(reset=reset, cmd=cmd, doc=doc)

    def client_go_generate(self, reset=False, package='client', import_path='', lib_root_urls=''):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml generate_goclient
        """

        cmd = self._get_cmd(package=package, import_path=import_path, lib_root_urls=lib_root_urls)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='go',
                         import_path=import_path, urls=lib_root_urls, package=package, type='client')
        self._client_generate(reset=reset, cmd=cmd)

    def client_nim_generate(self, reset=False):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml generate_goclient
        """
        cmd = self._get_cmd()
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='nim', type='client')
        self._client_generate(reset=reset, cmd=cmd)

    def server_python_generate(self, reset=False, kind='requests',
                               no_apidocs=False, no_main=False, lib_root_urls=''):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        supported_map = {
            'gevent': 'gevent-flask',
            'flask': 'flask',
            'sanic': 'sanic',
        }
        kind = self._get_kind(supported_map, kind)
        cmd = self._get_cmd(kind=kind, no_apidocs=no_apidocs, no_main=no_main, lib_root_urls=lib_root_urls)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='python',
                         kind=kind, urls=lib_root_urls, type='server')

        self._server_generate(reset=reset, cmd=cmd)

    def server_go_generate(self, reset=False, package='server', no_main=False, no_apidocs=False, import_path='',
                           lib_root_urls='', api_file_per_method=True):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        cmd = self._get_cmd(package=package, no_apidocs=no_apidocs, no_main=no_main, import_path=import_path,
                            lib_root_urls=lib_root_urls, api_file_per_method=api_file_per_method)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='go', package=package,
                         import_path=import_path, urls=lib_root_urls, type='server')

        self._server_generate(reset=reset, cmd=cmd)

    def server_lua_generate(self, reset=False):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        cmd = self._get_cmd()
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='tarantool', type='server')
        self._server_generate(reset=reset, cmd=cmd)

    def server_nim_generate(self, reset=False):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        cmd = self._get_cmd()
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='nim', type='server')
        self._server_generate(reset=reset, cmd=cmd)

    def server(self):
        cmd = "cd %s;sh start_server.sh" % self.path
        j.sal.process.executeInteractive(cmd)
