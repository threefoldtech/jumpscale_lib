from JumpScale9Lib.clients.ays import Client

BASE_URI = "https://localhost:5000"

class ClientFactory:

    def __init__(self):
        self.__jslocation__ = 'j.clients.ays'

    def get(self, base_uri=BASE_URI, jwt=None):
        return Client(self, base_uri, jwt)
