from js9 import j
import cryptocompare

TEMPLATE = """
api_key_ = ""
"""

JSConfigClient = j.tools.configmanager.base_class_config
JSConfigFactory = j.tools.configmanager.base_class_configs

from pprint import pprint as print



class CurrencyLayerFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.currencylayer"
        JSConfigFactory.__init__(self, CurrencyLayerClient)

class CurrencyLayerClient(JSConfigClient):
    """
    get key from https://currencylayer.com/quickstart
    """

    def __init__(self, instance, data={}, parent=None, interactive=True):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self._data_cur = {}
        self._id2cur = {}
        self._cur2id = {}
        self.fallback = True
        self.fake = False

    def load(self):
        def get():
            if self.fake==False and j.sal.nettools.tcpPortConnectionTest("currencylayer.com", 443):
                key = self.config.data["api_key_"]
                if key.strip()=="":
                    raise RuntimeError("api key for currency layer needs to be specified")
                url = "http://www.apilayer.net/api/live?access_key=%s" % key
                c = j.clients.http.getConnection()
                r = c.get(url).readlines()
                data = j.data.serializer.json.loads(r[0].decode())["quotes"]
                self.logger.info("fetch currency from internet")

                # add supported crypto currencies
                ETH = cryptocompare.get_price('USD', 'ETH')['USD']['ETH']
                data['USDETH'] = ETH
                XRP = cryptocompare.get_price('USD', 'XRP')['USD']['XRP']
                data['USDXRP'] = XRP
                # TODO: add tft 
                return data
            else:
                if self.fake or self.fallback:
                    self.logger.warning("cannot reach: currencylayer.com, use fake local data.")
                    from .currencies import currencies
                    return currencies
                raise RuntimeError("could not data from currencylayers")

        data = self.cache.get("currency_data", get, expire=3600 * 24)
        for key, item in data.items():
            if key.startswith("USD"):
                key = key[3:]
            self._data_cur[key.lower()] = item

    @property
    def cur2usd(self):
        """
        e.g. AED = 3,672 means 3,6... times AED=1 USD

        js9 'j.clients.currencylayer.cur2usd_print()'
        """
        if self._data_cur == {}:
            self.load()
        return self._data_cur

    def cur2usd_print(self):
        print(self.cur2usd)

    @property
    def id2cur(self):
        """
        """
        # def produce(): #ONLY DO THIS ONCE EVER !!!
        #     keys = [item for item in self.cur2usd.keys()]
        #     keys.sort()
        #     nr=0
        #     res={}
        #     for key in keys:
        #         nr+=1
        #         res[nr] = key
        #     return res
        if self._id2cur == {}:
            from .currencies_id import currencies_id
            self._id2cur = currencies_id
        return self._id2cur

    @property
    def cur2id(self):
        """
        """
        # def produce(): #ONLY DO THIS ONCE EVER !!!
        #     keys = [item for item in self.cur2usd.keys()]
        #     keys.sort()
        #     nr=0
        #     res={}
        #     for key in keys:
        #         nr+=1
        #         res[nr] = key
        #     return res
        if self._cur2id == {}:
            res = {}
            for key, val in self.id2cur.items():
                res[val] = key
            self._cur2id = res
        return self._cur2id

    def id2cur_print(self):
        """
        js9 'j.clients.currencylayer.id2cur_print()'
        """
        print(self.id2cur)

    def cur2id_print(self):
        """
        js9 'j.clients.currencylayer.cur2id_print()'
        """
        print(self.cur2id)


    def test(self):
        """
        js9 'j.clients.currencylayer.test()'
        """
        self.logger.error(self.cur2usd)
        assert 'aed' in self.cur2usd
