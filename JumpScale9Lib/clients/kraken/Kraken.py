from js9 import j

TEMPLATE = """
api_key_ = ""
private_key_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class Kraken(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = 'j.clients.kraken'
        JSConfigBase.__init__(self)
        self._config = j.tools.configmanager._get_for_obj(self, instance="main", data={}, template=TEMPLATE)

    def install(self):
        j.tools.prefab.local.runtimes.pip.install("pykrakenapi")
        j.tools.prefab.local.runtimes.pip.install("krakenex")

    def get(self):
        import krakenex
        from pykrakenapi import KrakenAPI
        api = krakenex.API()
        api.key=self.config.data["api_key_"]
        api.secret=self.config.data["private_key_"]
        k = KrakenAPI(api)
        return k

    def test(self):

        k=self.get()


        print ("open orders")
        print(k.get_open_orders())

        print("get account balance")
        print(k.get_account_balance())


