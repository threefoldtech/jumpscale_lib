from js9 import j

from http.client import HTTPSConnection


JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
bot_token_ = ""
"""


class TelegramBotFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.telegram_bot"
        JSConfigFactory.__init__(self, TelegramBot)


class TelegramBot(JSConfigClient):

    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE)
        self.logger = j.logger.get("j.clients.telegram_bot")
        self._conn =  HTTPSConnection("api.telegram.org")

    def config_check(self):
        """
        check the configuration if not what you want the class will barf & show you where it went wrong
        """
        if not self.config.data["bot_token_"]:
            return "bot_token_ is not properly configured, cannot be empty"

    def send_message(self, chatid, text):
        """
        send_message sends text to chat id
        :param chatid: Unique identifier for the target chat or username of the target channel
        :param text: Text of the message to be sent
        :return: result of sendMessage api
        """
        url = "/bot{}/sendMessage?chat_id={}&text={}".format(
            self.config.data["bot_token_"], chatid, text)
        return self._conn.request("GET", url)
