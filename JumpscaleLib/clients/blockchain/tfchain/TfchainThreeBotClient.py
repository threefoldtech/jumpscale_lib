from Jumpscale import j

import re
import requests

from JumpscaleLib.clients.blockchain.tfchain.TfchainNetwork import TfchainNetwork
from JumpscaleLib.clients.blockchain.tfchain.types import signatures as tftsig
from JumpscaleLib.clients.blockchain.rivine.errors import RESTAPIError
from JumpscaleLib.clients.blockchain.rivine.types import transaction
from JumpscaleLib.clients.blockchain.rivine import RivineWallet

class TfchainThreeBotClient():
    __bot_name_pattern = re.compile(r"^[A-Za-z]{1}[A-Za-z\-0-9]{3,61}[A-Za-z0-9]{1}(\.[A-Za-z]{1}[A-Za-z\-0-9]{3,55}[A-Za-z0-9]{1})*$")
    
    @staticmethod
    def get_record(id, network_addresses=None):
        """
        Get a 3Bot record registered on a TFchain network

        @param id: unique 3Bot id, public key or name to search a 3Bot record for, in string format
        @param network_addresses: network addresses from which to get the 3bot record
        """
        if not network_addresses:
            network_addresses = TfchainNetwork.STANDARD.official_explorers()

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
    
    # TODO: it might be useful to also allow the usage of spendable keys not related to the given wallet, currently this is not Possible
    @staticmethod
    def create_record(wallet, months=1, names=None, addresses=None, public_key=None):
        # create the tx and fill the easiest properties already
        tx = transaction.TransactionV144()
        tx.set_number_of_months(months)

        # add names and/or addresses
        if names:
            for name in names:
                tx.add_name(name)
        if addresses:
            for addr in addresses:
                tx.add_address(addr)

        # add coin inputs for miner fees (implicitly computed) and required bot fees
        input_results, used_addresses, minerfee, remainder = wallet._get_inputs(amount=tx.required_bot_fees)
        tx.set_transaction_fee(minerfee)
        for input_result in input_results:
            tx.add_coin_input(**input_result)
        for txn_input in tx.coin_inputs:
            if used_addresses[txn_input.parent_id] not in wallet._keys:
                raise RivineWallet.NonExistingOutputError('Trying to spend unexisting output')
        # optionally add the remainder as a refund coin output
        if remainder > 0:
            tx.set_refund_coin_output(value=remainder, recipient=wallet.addresses[0])

        # set the public key (used to sign using the wallet)
        foo = ''
        if not public_key:
            key = wallet.generate_key()
            public_key = key.public_key
        pk = tftsig.SiaPublicKey(tftsig.SiaPublicKeySpecifier.ED25519, public_key)
        tx.set_public_key(pk)

        # sign and commit the Tx, return the tx ID afterwards
        wallet.sign_transaction(transaction=tx, commit=True)
        return tx.id
