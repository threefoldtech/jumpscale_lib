from js9 import j
from zerorobot.dsl.ZeroRobotClient import ZeroRobotClient

SecretConfigBase = j.tools.secretconfig.base_class_secret_config
_template = """
base_url = "http://localhost:6600"
"""


class ZeroRobotFactory(SecretConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zrobot"
        self._TEMPLATE = _template

    def get(self, instance='main'):
        """
        Get a ZeroRobot client for base_url.
        """
        self.instance = instance
        base_url = self.config.data['base_url']
        return ZeroRobotClient(base_url)

    def set(self, instance, client):
        """
        associate an instance name with an instance of the client
        """

        sc = j.tools.secretconfig.set(self.__jslocation__, instance)
        sc.data = {'base_url': client._client.api.base_url}
        cfg.save()
