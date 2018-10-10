import uuid

from Jumpscale import j

from .ZDBClient import ZDBClient
from .ZDBClientNS import ZDBClientNS

JSConfigBase = j.tools.configmanager.JSBaseClassConfigs


class ZDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        super(ZDBFactory, self).__init__(ZDBClient)
        self._ZDBClientClass = ZDBClient
        self._ZDBClientNSClass = ZDBClientNS

    def configure(self, instance="main", secrets="", addr="localhost", port=None,
                  adminsecret="", mode="user"):
        """

        :param instance:
        :param secrets: $ns:$secret,... or $secret which will be defaulf for all namespaces
        :param addr:
        :param port:
        :param adminsecret: the main secret
        :param mode: seq or user
        :return:
        """

        if port is None:
            raise InputError("port cannot be None")

        data = {}
        data["addr"] = addr
        data["port"] = str(port)
        data["mode"] = str(mode)
        data["adminsecret_"] = adminsecret
        data["secrets_"] = secrets  #is now multiple secrets or 1 default one, in future will be our own serializion lib (the schemas)
        return self.get(instance=instance, data=data, create=True, interactive=False)

    def testdb_server_start_client_get(self,reset=False,mode="seq"):
        """
        will start a ZDB server in tmux (will only start when not there yet or when reset asked for)
        erase all content
        and will return client to it

        """

        db = j.servers.zdb.configure(instance="test", adminsecret="123456", reset=reset, mode=mode)
        db.start()

        #if secrets only 1 secret then will be used for all namespaces
        cl = db.client_get(secrets="1234")
        return cl

    def test(self):
        """
        js_shell 'j.clients.zdb.test()'

        """

        # create a random namespace
        def random_string(length=10):
            return str(uuid.uuid4()).replace('-', '')[:length]

        cl = j.clients.zdb.testdb_server_start_client_get(reset=True,mode="seq")

        cl1 = cl.namespace_new("test")
        # cl1.test_seq()

        print(cl1.meta)

        assert cl1.meta.config_exists("testa") == False
        cl1.meta.config_set("testa",1)
        assert cl1.meta.config_exists("testa") == True
        assert cl1.meta.config_get("testa") == 1

        cl1.meta.save()

        cl1._meta=None

        cl1.meta.load()

        assert cl1.meta.config_get("testa") == 1

        SCHEMA = """
        @url = jumpscale.schema.test.a
        category*= ""
        data = ""        
        """
        s = j.data.schema.get(SCHEMA)

        id = cl1.meta.schema_set(s)

        cl1._meta=None

        data_compare = {'md5': 'cd95678ef4fb17a7315970455f2ade93',
              'url': 'jumpscale.schema.test.a',
              'schema': '@url = jumpscale.schema.test.a\ncategory*= ""\ndata = ""        \n\n'}

        id, data = cl1.meta.schema_data_get(id=id)
        assert id==1
        assert data == data_compare

        id, data = cl1.meta.schema_data_get(md5='cd95678ef4fb17a7315970455f2ade93')
        assert id==1
        assert data == data_compare

        id, data = cl1.meta.schema_data_get(url='jumpscale.schema.test.a')
        assert id==1
        assert data == data_compare

        schemas = cl1.meta.schemas_get()

        assert len(schemas) == 1

        schema2=cl1.meta.schemas[1]  #schemas are on meta layer, id holds the schema

        assert len(schema2.properties)==2  #not very complete test

        print("TEST OK")

        #TODO: *1 need to test the other modes as well
