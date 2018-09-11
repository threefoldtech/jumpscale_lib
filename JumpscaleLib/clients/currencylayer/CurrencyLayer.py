import cryptocompare as cc
from Jumpscale import j
TEMPLATE = """
api_key_ = ""
"""

JSConfigBase = j.tools.configmanager.JSBaseClassConfig
JSBASE = j.application.JSBaseClass

from pprint import pprint as print


class CurrencyLayer(JSConfigBase):
    """
    get key from https://currencylayer.com/quickstart
    """

    def __init__(self):
        self.__jslocation__ = 'j.clients.currencylayer'
        JSConfigBase.__init__(self, instance="main", data={},
                              parent=None, template=TEMPLATE)
        self._data_cur = {}
        self._id2cur = {}
        self._cur2id = {}
        self.fallback = True
        self.fake = False

    def write_default(self):
        """ will load currencies from internet and then write to currencies.py 
            in the extension directory
        """
        raise NotImplementedError()
        #TODO:*2

    def load(self,reset=False):
        """ js_shell 'j.clients.currencylayer.load()'
        """
        if reset:
            self.cache.reset()
        def get():
            if not self.fake and \
                j.sal.nettools.tcpPortConnectionTest("currencylayer.com", 443):
                key = self.config.data["api_key_"]
                if key.strip():
                    url = "http://apilayer.net/api/live?access_key=%s" % key

                    c = j.clients.http.getConnection()
                    r = c.get(url).readlines()

                    data = r[0].decode()
                    data = j.data.serializers.json.loads(data)["quotes"]

                    data['USDETH'] = 1/cc.get_price('ETH','USD')['ETH']['USD']
                    data['USDXRP'] = cc.get_price('USD', 'XRP')['USD']['XRP']
                    data['USDBTC'] = 1/cc.get_price('BTC','USD')['BTC']['USD']

                    self.logger.error("fetch currency from internet")
                    return data
                elif not self.fallback:
                    raise RuntimeError("api key for currency layer "
                                        "needs to be specified")
                else:
                    self.logger.warning("currencylayer api_key not set, "
                                    "use fake local data.")

            if self.fake or self.fallback:
                self.logger.warning("cannot reach: currencylayer.com, "
                                "use fake local data.")
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

        js_shell 'j.clients.currencylayer.cur2usd_print()'
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
        js_shell 'j.clients.currencylayer.id2cur_print()'
        """
        pprint(self.id2cur)

    def cur2id_print(self):
        """
        js_shell 'j.clients.currencylayer.cur2id_print()'
        """
        pprint(self.cur2id)


    def test(self):
        """
        js_shell 'j.clients.currencylayer.test()'
        """
        self.logger.info(self.cur2usd)
        assert 'aed' in self.cur2usd
