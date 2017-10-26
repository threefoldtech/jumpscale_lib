from js9 import j

import packet


class PacketNetFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.packetnet"
        self.__imports__ = "packet"
        self.logger = j.logger.get('j.clients.packetnet')
        self.connections = {}

    def get(self, auth_token=""):
        """
        """
        if auth_token is "":
            auth_token = j.core.state.config["packetnet"]["apitoken"]
        return packet.Manager(auth_token=auth_token)
