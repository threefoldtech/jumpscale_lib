from Jumpscale import j

JSBASE = j.application.JSBaseClass


class OpenRestyFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.servers.openresty"

        JSBASE.__init__(self)
        self.latest = None

        self.logger_enable()


    def install(self):
        """
        js_shell 'j.servers.openresty.install()'

        """
        p = j.tools.prefab.local

        if p.core.doneGet("openresty") is False:

            if p.platformtype.isMac:

                self.logger.info("INSTALLING OPENRESTY")

                # will make sure we have the lobs here for web
                d = j.clients.git.getContentPathFromURLorPath("https://github.com/threefoldtech/openresty_build_osx")

                p.core.run("cd %s;bash install.sh"%d)

            else:
                C="""
                wget -qO - https://openresty.org/package/pubkey.gpg | sudo apt-key add -
                apt-get -y install software-properties-common
                add-apt-repository -y "deb http://openresty.org/package/ubuntu $(lsb_release -sc) main"
                apt-get update
                apt install openresty -y
                            
                ln -s /usr/local/openresty/luajit/bin/luajit /usr/local/bin/lua
                
                apt install luarocks -y
                
                
                apt install openresty-openssl-dev
                luarocks install luaossl OPENSSL_DIR=/usr/local/openresty/openssl CRYPTO_DIR=/usr/local/openresty/openssl
                luarocks install lapis
                luarocks install moonscript
                luarocks install lapis-console
                 
                """
                p.core.execute_bash(C)

                d = j.clients.git.getContentPathFromURLorPath("https://github.com/threefoldtech/openresty_build_osx")

                src_config_nginx = j.sal.fs.joinPaths(j.dirs.CODEDIR,"github/threefoldtech/openresty_build_osx/cfg")
                j.sal.fs.copyDirTree(src_config_nginx, "/etc/openresty", keepsymlinks=False, deletefirst=True)

                j.shell()
                raise RuntimeError("only osx supported for now")

            p.core.doneSet("openresty")

    def start(self):
        """
        :return:
        """


        self.install()


        self.process = j.servers.jsrun.get(name="openresty",
                                cmd="openresty",path="/tmp",ports=[8081],
                                stopcmd="openresty -s stop",
                                process_strings = ["nginx","openresty"],
                                reset=False)
        self.process.start()

    # def config_set(self,name,configstr):
    #     """
    #
    #     :param name: name of the configuration string
    #     :param configstr: the code of the config itself
    #
    #     e.g.
    #     ```
    #    location /static/ {
    #         root   {j.dirs.VARDIR}/www;
    #         index  index.html index.htm;
    #     }
    #
    #     ```
    #
    #     :return:
    #     """
    #
    #     j.shell()


    def configs_add(self,path,args={}):
        args["j"]=j

        if j.core.platformtype.myplatform.isMac:
            dest="/usr/local/etc/openresty/configs/"
        else:
            dest="/etc/openresty/configs/"

        j.tools.jinja2.copy_dir_render(path,dest,overwriteFiles=True,reset=True,render=True,**args)

    def reload(self):
        """
        :return:
        """
        cmd="openresty -s reload"
        j.sal.process.execute(cmd)
