from Jumpscale import j

JSBASE = j.application.JSBaseClass


class ZDBServer(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.zdb"
        JSBASE.__init__(self)
        self.configure()
        self.logger_enable()

    def configure(self,name="main",addr="localhost",port=9901,datadir="",mode="seq",adminsecret="1234"):
        self.name=name
        self.addr=addr
        self.port=port
        if datadir=="":
            self.datadir = j.sal.fs.joinPaths(j.dirs.DATADIR, 'zdb', name)
        else:
            self.datadir = datadir
        self.mode=mode
        self.adminsecret=adminsecret

    def start(self,reset=False):
        """
        start zdb in tmux using this directory (use prefab)
        will only start when the server is not life yet

        :param self.name:
        :param self.addr:
        :param self.port:
        :param self.datadir:
        :param self.mode:
        :param self.adminsecret:
        :return:
        """

        j.sal.fs.createDir(self.datadir)

        if j.sal.nettools.tcpPortConnectionTest(self.addr,self.port):
            r=j.clients.redis.get(ipaddr=self.addr, port=self.port)
            r.ping()
            return()

        if reset:
            self.destroy()


        if j.core.platformtype.myplatform.isMac and self.addr=="localhost":
            self.addr="127.0.0.1"

        j.tools.prefab.local.zero_os.zos_db.start(instance=self.name,
                                                  host=self.addr,
                                                  port=self.port,
                                                  index=self.datadir,
                                                  data=self.datadir,
                                                  verbose=True,
                                                  mode=self.mode,
                                                  adminsecret=self.adminsecret)

        self.logger.info("waiting for zdb server to start on (%s:%s)" % (self.addr, self.port))

        res = j.sal.nettools.waitConnectionTest(self.addr, self.port)
        if res is False:
            raise RuntimeError("could not start zdb:'%s' (%s:%s)" % (self.name, self.addr, self.port))


    def stop(self):
        j.tools.prefab.local.zero_os.zos_db.stop(self.name)

    def destroy(self):
        self.stop()
        j.sal.fs.removeDirTree(self.datadir)
        ipath = j.dirs.VARDIR + "/zdb/index/%s.db" % self.name
        j.sal.fs.remove(ipath)


    def client_admin_get(self):
        """

        """
        cl =  j.clients.zdb.client_admin_get(addr=self.addr,
                                       port=self.port,
                                       secret=self.adminsecret,
                                       mode = self.mode)
        return cl

    def client_get(self, nsname="default", secret="1234"):
        """
        get client to zdb

        """

        cla = self.client_admin_get()

        if nsname not in ["default"]:
            cla.namespace_new(nsname,secret=secret)
        else:
            secret = self.adminsecret

        cl =  j.clients.zdb.client_get(nsname=nsname,addr=self.addr,port=self.port,secret=secret,mode=self.mode)

        assert cl.ping()

        return cl


    def start_test_instance(self,reset=False):
        """
        start a test instance with self.adminsecret 123456
        will use port 9900
        and name = test

        production is using other ports and other secret

        :return:
        """
        self.name = "test"
        self.port = 9900
        self.mode = "seq"
        self.adminsecret = "123456"
        if reset:
            cla=self.client_admin_get()
            cla.reset()
        self.start()
        return self


    def build(self):
        """
        js_shell 'j.servers.zdb.build()'
        """
        j.tools.prefab.local.zero_os.zos_db.build(install=True,reset=True)

    def test(self,build=False):
        """
        js_shell 'j.servers.zdb.test(build=True)'
        """
        if build:
            self.build()
        self.start_test_instance()
        self.destroy()
        self.stop()
        self.start()
        cl=self.client_get(nsname="test")

        print("TEST OK")

