from js9 import j
from JumpScale9Lib.clients.cockpit.client import Client
import requests


class CockpitFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.cockpit"
        self.__imports__ = "requests"

    def getClient(self, base_uri, jwt, verify_ssl=True):
        return Client(base_uri=base_uri, jwt=jwt, verify_ssl=verify_ssl)

    def get(self, base_uri, jwt, verify_ssl=True):
        return Client(base_uri=base_uri, jwt=jwt, verify_ssl=verify_ssl)
