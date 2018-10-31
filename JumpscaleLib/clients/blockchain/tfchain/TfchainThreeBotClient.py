from Jumpscale import j

import re
import requests

from JumpscaleLib.clients.blockchain.tfchain.TfchainNetwork import TfchainNetwork
from JumpscaleLib.clients.blockchain.rivine.errors import RESTAPIError

class TfchainThreeBotClient():
    __bot_name_pattern = re.compile(r"^[A-Za-z]{1}[A-Za-z\-0-9]{3,61}[A-Za-z0-9]{1}(\.[A-Za-z]{1}[A-Za-z\-0-9]{3,55}[A-Za-z0-9]{1})*$")
    
    @staticmethod
    def get_record(id, network_addresses=TfchainNetwork.STANDARD.official_explorers()):
        """
        Get a 3Bot record registered on a TFchain network

        @param id: unique 3Bot id, public key or name to search a 3Bot record for, in string format
        @param network_addresses: network addresses from which to get the 3bot record
        """
        msg = 'Failed to retrieve 3Bot record.'
        result = None
        response = None
        endpoint = "explorer/3bot"
        if isinstance(id, str) and TfchainThreeBotClient.__bot_name_pattern.match(id):
            endpoint = "explorer/whois/3bot"
        for address in network_addresses:
            url = '{}/{}/{}'.format(address.strip('/'), endpoint, id)
            headers = {'user-agent': 'Rivine-Agent'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                continue
            if response.status_code == 200:
                result = response.json()
                break

        if result is None:
            if response:
                raise RESTAPIError('{} {}'.format(msg, response.text.strip('\n')))
            else:
                raise RESTAPIError(msg)
        return result
    
    @staticmethod
    def create_record(wallet, ...)
        TODO
