from js9 import j

JSBASE = j.application.jsbase_get_class()


class Config(JSBASE):

    def __init__(self, client):
        self._client = client
        JSBASE.__init__(self)

    def get(self):
        """
        Get the config of g8os
        """
        return self._client.json('config.get', {})

