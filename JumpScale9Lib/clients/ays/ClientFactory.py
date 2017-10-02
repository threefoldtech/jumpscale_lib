from JumpScale9Lib.clients.ays import Client

class ClientFactory:

    def __init__(self):
        self.__jslocation__ = 'j.clients.ays'

    def get(self):
        return Client()
