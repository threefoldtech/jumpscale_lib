from .GogsClient import GogsClient
from js9 import j


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.__imports__ = "requests,psycopg2"
        self.logger = j.logger.get("j.clients.gogs")

    def getRestClient(self, addr='https://127.0.0.1', port=3000, login='root', passwd='root', accesstoken=None):
        """
        # Getting client via accesstoken

        # Create access token in gogs

        Under user profile click your settings.
        Click Applications, from there use generate new token to create your token.

        # User Access token
        rest = j.clients.gogs.getRestClient('https://docs.greenitglobe.com', 443,
                                            accesstoken='myaccesstoken')

        # Getting client via username, password
        rest = j.clients.gogs.getRestClient('https://docs.greenitglobe.com', 443,
                                            'myusername', 'mypassword')

        """
        return GogsClient(addr=addr, port=port, login=login, passwd=passwd, accesstoken=accesstoken)
