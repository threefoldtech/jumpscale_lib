from .client import Client

DEFAULT_URL = "https://localhost:5000"

class ClientFactory:

    def __init__(self):
        self.__jslocation__ = 'j.clients.ays'

    def get(self, url=DEFAULT_URL, jwt=None):
        """
        Get an AYS client to interact with a local or remote AYS server.

        Args:
            url: url of the AYS RESTful API, e.g. `http://172.25.0.238:5000`; defaults to https://localhost:5000
            jwt: JSON Web Token for the ItsYou.online organization protecting the AYS RESTful API; defaults to None
        """
        return Client(url=url, jwt=jwt, clientID=None, secret=None, validity=None)

    def getWithClientID(self, clientID, secret, url=DEFAULT_URL, validity=3600):
        """
        Get an AYS client to interact with a local or remote AYS server.

        Args:
            url: url of the AYS RESTful API, e.g. `http://172.25.0.238:5000`; defaults to https://localhost:5000
            clientID: client ID of the API access key of the ItsYou.online organization protecting the AYS RESTful API; defaults to None
            secret: secret of the API access key of the ItsYou.online organization protecting the AYS RESTful API; defaults to None
            validity: validity of the JWT that will be created based on the given client ID and secret, defaults to 3600 (seconds)
        """
        return Client(url=url, jwt=None, clientID=clientID, secret=secret, validity=validity)