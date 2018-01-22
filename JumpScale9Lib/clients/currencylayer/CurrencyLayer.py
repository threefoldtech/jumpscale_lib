from js9 import j

TEMPLATE = """
api_key_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class CurrencyLayer(JSConfigBase):
    """
    get key from https://currencylayer.com/quickstart
    """

    def __init__(self):
        self.__jslocation__ = 'j.clients.currencylayer'
        JSConfigBase.__init__(self, instance="main", data={}, parent=None,template=TEMPLATE)
        self._data_cur={}
        self.cache = j.data.cache.redis_local_get()

    def load(self):
        def get():
            key=self.config.data["api_key_"]
            url="http://www.apilayer.net/api/live?access_key=%s"%key
            c=j.clients.http.getConnection()
            r=c.get(url).readlines()
            data=j.data.serializer.json.loads(r[0].decode())["quotes"]
            print ("fetch currency from internet")
            return data
        data = self.cache.get("currency_data", get, expire=3600*24)

        for key,item in data.items():
            if not key.startswith("USD"):
                raise RuntimeError("data not ok, needs to start from USD")
            key=key[3:]
            self._data_cur[key.lower()]=item

    @property
    def cur2usd(self):
        """
        e.g. AED = 3,672 means 3,6... times AED=1 USD
        """
        if self._data_cur=={}:
            self.load()
        return self._data_cur

    def test(self):
        """
        js9 'j.clients.currencylayer.test()'
        """
        print (self.cur2usd)
        assert 'AED' in self.cur2usd

