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
                raise RuntimeError("only osx supported for now")

            p.core.doneSet("openresty")

    def start(self):
        """
        :param path: directory where the nginx configs are
        :return:
        """


        self.install()


        self.process = j.servers.jsrun.get(name="openresty",
                                cmd="openresty",path="/tmp",ports=[8081],
                                stopcmd="openresty -s stop",
                                process_strings = ["nginx","openresty"],
                                reset=False)
        self.process.start()



