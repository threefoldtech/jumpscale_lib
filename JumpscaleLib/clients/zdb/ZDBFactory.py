import os
import uuid
from pprint import pprint

from Jumpscale import j

from .ZDBAdminClient import ZDBAdminClient
from .clients_impl import ZDBClientDirectMode, ZDBClientSeqMode, ZDBClientUserMode

JSBASE = j.application.JSBaseClass


_client_map = {
    'seq': ZDBClientSeqMode,
    'sequential': ZDBClientSeqMode,
    'user': ZDBClientUserMode,
    'direct': ZDBClientDirectMode,
}


class ZDBFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        JSBASE.__init__(self)

    def client_admin_get(self, addr="localhost", port=9900, secret="123456", mode='seq'):
        return ZDBAdminClient(addr=addr, port=port, secret=secret, mode=mode)

    def client_get(self, nsname="test", addr="localhost", port=9900, secret="1234", mode="seq"):
        """
        :param nsname: namespace name
        :param addr:
        :param port:
        :param secret:
        :return:
        """
        if mode not in _client_map:
            return ValueError("mode %s not supported" % mode)
        klass = _client_map[mode]
        return klass(addr=addr, port=port, secret=secret, nsname=nsname)

    def testdb_server_start_client_admin_get(self, reset=False, mode="seq", secret="123456"):
        """
        will start a ZDB server in tmux (will only start when not there yet or when reset asked for)
        erase all content
        and will return client to it

        """

        j.servers.zdb.mode = mode
        j.servers.zdb.name = "test"

        j.servers.zdb.start(reset=reset)

        # if secrets only 1 secret then will be used for all namespaces
        cl = self.client_admin_get(secret=secret)
        return cl

    def _test_admin(self):
        """
        js_shell 'j.clients.zdb._test_admin()'

        """

        c = self.client_admin_get()
        c.reset()

        c.namespaces_list()
        assert c.namespaces_list() == ['default']

    def test(self, start=True):
        """
        js_shell 'j.clients.zdb.test(start=True)'

        """

        if start:
            j.clients.zdb.testdb_server_start_client_admin_get(reset=True, mode="seq")

        self._test_admin()

        c = self.client_admin_get()
        c.namespace_new("test", secret="1234")

        cl1 = self.client_get()

        self._test_seq(cl1)

        print(cl1.meta)

        assert cl1.meta.config_exists("testa") == False
        cl1.meta.config_set("testa", 1)
        assert cl1.meta.config_exists("testa") == True
        assert cl1.meta.config_get("testa") == 1

        cl1.meta.save()

        cl1._meta = None

        cl1.meta.load()

        assert cl1.meta.config_get("testa") == 1

        SCHEMA = j.core.text.strip("""
        @url = jumpscale.schema.test.a
        category*= ""
        data = ""
        """)
        s = j.data.schema.get(SCHEMA)

        id = cl1.meta.schema_set(s)

        cl1._meta = None

        data_compare = {'md5': '4ab4a8b1c8073b4698461a1eafbad161',
                        'url': 'jumpscale.schema.test.a',
                        'schema': '@url = jumpscale.schema.test.a\ncategory*= ""\ndata = ""\n\n'}

        id, data = cl1.meta.schema_data_get(id=id)
        assert id == 1
        assert data == data_compare

        id, data = cl1.meta.schema_data_get(md5='4ab4a8b1c8073b4698461a1eafbad161')
        assert id == 1
        assert data == data_compare

        id, data = cl1.meta.schema_data_get(url='jumpscale.schema.test.a')
        assert id == 1
        assert data == data_compare

        schemas = cl1.meta.schemas_load()

        assert len(schemas) == 1

        schema2 = cl1.meta.schemas[1]  # schemas are on meta layer, id holds the schema

        assert len(schema2.properties) == 2  # not very complete test

        print("TEST OK")

    def _test_seq(self, cl):

        nr = cl.nsinfo["entries"]
        assert nr == 1
        # do test to see that we can compare
        id = cl.set(b"r")
        assert id == 1
        assert cl.get(id) == b"r"

        id2 = cl.set(b"b")
        assert id2 == 2

        assert cl.set(b"r", key=id) is None
        assert cl.set(b"rss", key=id) == 1  # changed the data, returns id 1

        nr = cl.nsinfo["entries"]
        assert nr == 3  # nr of real data inside

        # test the list function
        assert cl.list() == [0, 1, 2]
        assert cl.list(2) == [2]
        assert cl.list(0) == [0, 1, 2]

        result = {}
        for id, data in cl.iterate():
            if id == 0:
                continue
            pprint("%s:%s" % (id, data))
            result[id] = data

        assert {1: b'rss', 2: b'b'} == result

        assert cl.list(key_start=id2)[0] == id2

        assert cl.exists(id2)

        print("write 10000 entries")

        def dumpdata(self):

            inputs = {}
            for i in range(1000):
                data = os.urandom(4096)
                key = cl.set(data)
                inputs[key] = data

            for k, expected in inputs.items():
                actual = cl.get(k)
                if expected != actual:
                    j.shell()
                    wac
                assert expected == actual

        dumpdata(self)  # is in default namespace

        pprint("count:%s" % cl.count)

        nsname = "newnamespace"

        c = self.client_admin_get()
        c.namespace_new(nsname, secret="1234", maxsize=1000)
        ns = self.client_get(nsname, secret="1234")

        assert ns.nsinfo["data_limits_bytes"] == 1000
        assert ns.nsinfo["data_size_bytes"] == 18
        assert ns.nsinfo["data_size_mb"] == 0.0
        assert int(ns.nsinfo["entries"]) == 1
        assert ns.nsinfo["index_size_bytes"] == 0
        assert ns.nsinfo["index_size_kb"] == 0.0
        assert ns.nsinfo["name"] == nsname
        assert ns.nsinfo["password"] == "yes"
        assert ns.nsinfo["public"] == "no"

        assert ns.nsname == nsname

        # both should be same
        id = ns.set(b"a")
        assert ns.get(id) == b"a"
        assert ns.nsinfo["entries"] == 2

        try:
            dumpdata(ns)
        except Exception as e:
            assert "No space left" in str(e)

        c.namespace_new(nsname + "2", secret="1234")

        nritems = 10000
        j.tools.timer.start("zdb")

        pprint("perftest for 10.000 records, should get above 10k per sec")
        for i in range(nritems):
            id = cl.set(b"a")

        j.tools.timer.stop(nritems)

        print ("TEST SEQ OK")
