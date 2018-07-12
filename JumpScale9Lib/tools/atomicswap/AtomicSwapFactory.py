"""
Factory Module for atomic swap
"""
from js9 import j
import re
import requests
import time
import json
import os



JSBASE = j.application.jsbase_get_class()

SUPPORTED_CURRENCIES = ['BTC', 'TFT']
DEFAULT_LOCKTIME_THRESHOLD = 25
HASTINGS_TFT_VALUE = 1000000000.0
DEFAULT_BTC_RPC_USER = 'user'
DEFAULT_BTC_RPC_PASS = 'pass'
DEFAULT_BTC_RPC_ADDRESS = 'localhost:8332'
DEFAULT_TFT_DAEMON_ADDRESS = 'localhost:23110'


def _execute_and_extract(prefab, cmd, regex, cmd_name, logger, test_output=None):
    """
    Executes a command via a prefab object, extract the data from the output that matches a regular expression
    """
    logger.debug('Executing command {}'.format(cmd))
    if test_output is not None:
        rc, out, err = 0, test_output, ""
    else:
        rc, out, err = prefab.core.run(cmd=cmd, showout=False)
    if rc:
        raise RuntimeError('Failed to execute {} step. Error {}'.format(cmd_name, '{}\n{}'.format(out,err)))
    match = re.search(regex, out)
    if not match:
        raise RuntimeError('Cannot parse the output of the {} step using output {}'.format(cmd_name, out))
    return match.groupdict()


def _tft_wait_for_height(prefab, height, timeout=None, daemon_address=None):
    """
    Will wait until the tft node reach the desired height

    @param prefab: Prefab object connected to the tft node
    @param height: The desired height to wait for
    @param timeout: If set, then we will wait max the amount of timeout and then we die if the node is not on the desired height
    """
    height_reached = False
    daemon_address = daemon_address or os.environ.get('TFT_DAEMON_ADDRESS', DEFAULT_TFT_DAEMON_ADDRESS)
    cmd = 'tfchainc -a {}'.format(daemon_address)
    while height_reached is False:
        if timeout is not None and timeout < 0:
            break
        _, out, err = prefab.core.run(cmd=cmd, showout=False, die=False)
        out = '{}\n{}'.format(out, err)
        match = re.search('^Synced:\s+(?P<synced>\w+)\n*.*\n*Height:\s*(?P<height>\d+)', out)
        if match:
            match_info = match.groupdict()
            if int(match_info['height']) >= height:
                height_reached = True
                continue
        time.sleep(10)
        if timeout is not None:
            timeout -= 10

    if timeout is not None and timeout < 0:
        raise RuntimeError("TIMEOUT: TFT node is out of sync and did not reach height {}".format(height))
    return True


def _get_prefab_from_address(address):
    """
    Parses an address of the format ip[:port] and return return a prefab object connected to the remote node
    """
    try:
        if ':' in address:
            ip, port = address.split(':')
            port = int(port)
        else:
            ip, port = address, 22
    except Exception:
        raise ValueError("Invalid node address")

    return j.tools.prefab.getFromSSH(addr=ip, port=port)




class AtomicSwapFactory(JSBASE):
    """
    Factory class for atomicswap tool
    """
    def __init__(self):
        self.__jslocation__ = "j.tools.atomicswap"
        JSBASE.__init__(self)

    def _check_amount_format(self, amount):
        """
        Check the amount format and returns the amount and the currency code

        @param amount: Amount in the format '0.0000XXX'

        @returns: Tuple with (amount, currency_code)
        """
        if len(amount) > 3:
            if amount[-3:].upper() in SUPPORTED_CURRENCIES:
                try:
                    actual_amount = float(amount[:-3])
                    return (actual_amount, amount[-3:].upper())
                except ValueError:
                    pass
        raise ValueError('Invlaid amount format')


    def _validate_initiate_audit(self, initiator, initiator_result, audit_result):
        """
        Validates an audit result against the pre-process initiate operation. It will validate the following:
            the locktime is far enough in the future
            the amount is correct
            the recipient is correct
        """
        errors = []
        matching_keys = ['secret_hash', 'contract_addr']
        for matching_key in matching_keys:
            if initiator_result[matching_key] != audit_result[matching_key]:
                errors.append('{} is not the same'.format(matching_key))
        if initiator._recipient_address != audit_result['recipient_addr']:
            errors.append('Recipient address is not correct when auditing the contract')
        if initiator._amount != float(audit_result['contract_value']):
            errors.append("Contract amount is not the same")
        hours = audit_result['remaining_locktime'].rsplit('h')
        if len(hours) < 2 or int(hours[0]) < DEFAULT_LOCKTIME_THRESHOLD:
            erros.append("Contract is not valid far enough in the future")
        if errors:
            raise RuntimeError("Invalide audit result. Errors: {}".format('\n'.join(errors)))



    def execute(self, initiator_prefab, initiator_address, initiator_amount, participant_prefab, participant_address, participant_amount, testnet=False):
        """
        Executes a full cross chains atomicswap operation. This might take a long time depending on the confirmation time that each blockchain
        netowrk will take.

        @param initiator_prefab: Prefab object connecting to the atomic swap initiator node
        @param initiator_address: Address from the participant network to recieve funds on
        @param initiator_amount: Amount in the initator currency in the format '0.00024XXX' where XXX is the currency code, must be one of the following
        ('BTC', 'TFT', 'ETH', 'XRP')
        @param participant_prefab: Prefab object connecting to  the atomic swap participant node.
        @param participant_address: Address from the initiator network to recieve funds on.
        @param participant_amount: Amount in the participant currency in the format '0.0000XXX' where XXX is the currency code, must be one of the following
        ('BTC', 'TFT', 'ETH', 'XRP')
        @param testnet: If True, testnet is going to be used when doing the atomicswap [False by default]
        """
        self.logger.info("Starting atomicswap operation")
        initiator_amount, initiator_currency = self._check_amount_format(initiator_amount)
        participant_amount, participant_currency = self._check_amount_format(participant_amount)
        if initiator_currency == participant_currency:
            raise RuntimeError('Initiator currency and participant currency cannot be the same.')
        # right now only BTC and TFT are supported for atomicswap
        if initiator_currency == 'BTC':
            initiator = BTCInitiator(prefab=initiator_prefab, recipient_address=participant_address,
                                    amount=initiator_amount, testnet=testnet)
            participant = TFTParticipant(prefab=participant_prefab, initiator_address=initiator_address,
                                        amount=participant_amount, testnet=testnet)
        else:
            initiator = BTCInitiator(prefab=participant_prefab, recipient_address=initiator_address,
                                    amount=participant_amount, testnet=testnet)
            participant = TFTParticipant(prefab=initiator_prefab, initiator_address=participant_address,
                                        amount=initiator_amount, testnet=testnet)

        # start initiate operation and wait for the published transaction to be confirmed
        self.logger.info("Intiating the atomicswap")
        initiate_result = initiator.initiate()
        initiator.wait_for_confirmations(transaction_id=initiate_result['published_contract_txn_address'])
        # participant audit the initiated contract
        audit_result = participant.auditcontract(contract=initiate_result['contract'], contract_txn=initiate_result['contract_txn'])

        self._validate_initiate_audit(initiator, initiate_result, audit_result)

        self.logger.info("Waiting for participant node to be synced")
        _tft_wait_for_height(prefab=participant_prefab, height=participant.get_current_chain_height())

        self.logger.info("Executing paricipate operation")
        participate_result = participant.participate(secret_hash=initiate_result['secret_hash'])

        participant.wait_for_confirmations(transaction_id=participate_result['transaction_id'])

        self.logger.info("Waiting for initiator node to be sycned")
        _tft_wait_for_height(prefab=initiator_prefab, height=participant.get_current_chain_height())
        initiator.auditcontract(output_id=participate_result['output_id'],
                                  recipient_addr=participate_result['recipient_addr'],
                                  secret_hash=participate_result['secret_hash'],
                                  amount=participate_result['contract_value'])

        #todo: we should validate the participate audit as well
        self.logger.info("Initiator redeeming the contract")
        redeem_output = initiator.redeem(output_id=participate_result['output_id'], secret=initiate_result['secret'])
        participant.wait_for_confirmations(transaction_id=redeem_output['transaction_id'])

        self.logger.info("Participant redeeming the contract")
        participant_redeem_result = participant.redeem(contract=initiate_result['contract'], contract_txn=initiate_result['contract_txn'], secret=initiate_result['secret'])
        initiator.wait_for_confirmations(transaction_id=participant_redeem_result['transaction_id'])


    def get_btc_initiator(self, wallet_node_address, amount, recipient_address, testnet=False):
        """
        Creates new BTCInitiator with the given parameters and return it

        @param wallet_node_address: ip[:port] formatted address to the remote node running the BTC daemon. if no port is given 22 will be used.
        @param amount: Amount of bitcoins to swap.
        @param recipient_address: Address in the BTC network to send the funds to.
        @param testnet: If True, then the bitcoin testnet will be used.

        @returns: BTCInitiator object exposing APIs to perform atomicswap operations
        """
        prefab = _get_prefab_from_address(wallet_node_address)
        return BTCInitiator(prefab=prefab, recipient_address=recipient_address,
                                amount=amount, testnet=testnet)

    def get_tft_participant(self, wallet_node_address, amount, recipient_address, testnet=False):
        """
        Creates new TFTParticipant with the given parameters and return it

        @param wallet_node_address: ip:port formatted address to the remote node running the TFChain daemon. if no port is given 22 will be used.
        @param amount: Amount of TFTs to swap.
        @param recipient_address: Address in the TFT network to send funds on.
        @param testnet: If True, then the tfchain testnet will be used.

        @returns: TFTParticipant object exposing APIs to perform atomicswap operations
        """
        prefab = _get_prefab_from_address(wallet_node_address)
        return TFTParticipant(prefab=prefab, initiator_address=recipient_address,
                              amount=amount, testnet=testnet)


class Initiator(JSBASE):
    """
    Initiator class
    """
    def __init__(self, prefab, recipient_address, amount, testnet=False):
        """
        Initializes an initiator
        """
        self._prefab = prefab
        self._recipient_address = recipient_address
        self._amount = amount
        self._testnet= testnet
        JSBASE.__init__(self)


class BTCInitiator(Initiator):
    """
    BTCInitiator class
    """
    BTC_TESTNET_EXPLORER_URL = 'https://testnet.blockexplorer.com/api/tx'
    BTC_EXPLORER_URl = 'https://blockexplorer.com/api/tx'
    BTC_MIN_CONFIRMATIONS = 6


    def wait_for_confirmations(self, transaction_id, nr_of_confirmations=None):
        """
        Waits until the transaction have specific number of confirmations

        @param transaction_id: ID of the transaction to check
        @param nr_of_confirmations: Number of confirmations to wait for
        """
        if nr_of_confirmations is None:
            nr_of_confirmations = int(os.environ.get('BTC_MIN_CONFIRMATIONS', self.BTC_MIN_CONFIRMATIONS))
            # nr_of_confirmations = self.BTC_MIN_CONFIRMATIONS
        self.logger.info("Waiting for transaction {} to have at least {} confirmations".format(transaction_id, nr_of_confirmations))
        not_found_timeout = 120
        url = '{}/{}'.format(self.BTC_TESTNET_EXPLORER_URL if self._testnet else self.BTC_EXPLORER_URl, transaction_id)
        while not_found_timeout > 0:
            res = requests.get(url)
            if res.status_code == 200:
                break
            else:
                not_found_timeout -= 20
                time.sleep(20)
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError("Cannot confirm transaction using {}".format(url))
        while res.json().get('confirmations', 0) < nr_of_confirmations:
            res = requests.get(url)
            time.sleep(20)


    def initiate(self, rpcuser=None, rpcpass=None, addr=None):
        """
        Initiate an atomic swap
        """
        rpcuser = rpcuser or os.environ.get('BTC_RPC_USER', DEFAULT_BTC_RPC_USER)
        rpcpass = rpcpass or os.environ.get('BTC_RPC_PASS', DEFAULT_BTC_RPC_PASS)
        addr = addr or os.environ.get('BTC_RPC_ADDRESS', DEFAULT_BTC_RPC_ADDRESS)
        cmd = 'btcatomicswap{} --rpcuser={} --rpcpass={} -s {} --force-yes initiate {} {}'.format(' --testnet' if self._testnet else '',
                rpcuser, rpcpass, addr, self._recipient_address, self._amount)
        pattern = r'Secret:\s*(?P<secret>\w+)\n*Secret\shash:\s*(?P<secret_hash>\w+)\n*.*\n*.*\n*Contract\s*\((?P<contract_addr>\w+)\):\n*(?P<contract>\w+)\n*Contract\s*transaction\s*\((?P<contract_txn_addr>\w+)\):\n*(?P<contract_txn>\w+)\n*Refund\s*transaction\s*\((?P<refund_txn_addr>\w+)\):\n*(?P<refund_txn>\w+)\n*.*\n*Published\s*contract\s*transaction\s*\((?P<published_contract_txn_address>\w+)\)'
        test_output=None
#         test_output="""
# Secret:      58febdffd0dd5c141d27c45d8fb1a962e2e9a4eb991fac2da0bca56bd99736ca
# Secret hash: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8
#
# Contract fee: 0.00000166 BTC (0.00000672 BTC/kB)
# Refund fee:   0.00000297 BTC (0.00001017 BTC/kB)
#
# Contract (2NFBadefP7PrqDWyyjfJZbvpJrs1Tx8BSke):
# 6382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac
#
# Contract transaction (a37d954d2cfc03526ebb0624e68389f9140f05ac19e5df03a58593204a1c2fd8):
# 0200000000010156901f407052d8c5185a54246e764d8304574aae13847c71ea5a2afb73d9e8e80000000017160014253584f1f207ff244c2d9dd10f2508b265f31395feffffff028a1be8020000000017a9144a0de4a6e8e5a52c7c249890a00c8bafa217510b8750d412000000000017a914f0a2561a9fd9de1ce4ee98f70de86ae3312f4873870247304402202761c014d6a3c69584d437153e0eb75f12e21f06ea267818bb7eca933ed892ef02201fd5ed6e24ae6fb684386a58cfcbbfde0ae1e16260bc52d3ce7e79a5e9ab98d80121031be3ad72917139bda0c3b4c3aa0e405772bb1b10168104604b4140eb7bf6338200000000
#
# Refund transaction (bda4c504b8ce4df6ac50e4914d16421c50ba4defb916e1142b5bcad25efede97):
# 0200000001d82f1c4a209385a503dfe519ac050f14f98983e62406bb6e5203fc2c4d957da301000000cf483045022100c367297bef6e53b5de7522c396979eac70e7d9eb62adf727083cf3ef777192c402201f799215dd284f2d3d3a6fd10453b83b28ac01e43e6e5a1ef5ef39b97b35c0cf0121028d69b6cdc4c6ed23170c0918388a6c9b27811372db9954d898affbcd40ede697004c616382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888ac000000000127d31200000000001976a914063f138942d2b2af935c678c2a99ae9470d8908e88acab0d045b
#
# Published contract transaction (a37d954d2cfc03526ebb0624e68389f9140f05ac19e5df03a58593204a1c2fd8)
# """

        return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="initiate", logger=self.logger, test_output=test_output)


    def participate(self, secret_hash, rpcuser=None, rpcpass=None, addr=None):
        """
        Participates in an atomicswap contract
        """
        rpcuser = rpcuser or os.environ.get('BTC_RPC_USER', DEFAULT_BTC_RPC_USER)
        rpcpass = rpcpass or os.environ.get('BTC_RPC_PASS', DEFAULT_BTC_RPC_PASS)
        addr = addr or os.environ.get('BTC_RPC_ADDRESS', DEFAULT_BTC_RPC_ADDRESS)
        cmd = 'btcatomicswap{} --rpcuser={} --rpcpass={} -s {} --force-yes participate {} {} {}'.format(' --testnet' if self._testnet else '',
                rpcuser, rpcpass, addr, self._recipient_address, self._amount, secret_hash)
        pattern = r'Contract\s*\((?P<contract_addr>\w+)\):\n*(?P<contract>\w+)\n*Contract\s*transaction\s*\((?P<contract_txn_addr>\w+)\):\n*(?P<contract_txn>\w+)\n*Refund\s*transaction\s*\((?P<refund_txn_addr>\w+)\):\n*(?P<refund_txn>\w+)\n*.*\n*Published\s*contract\s*transaction\s*\((?P<published_contract_txn_address>\w+)\)'
        test_output=None
#         test_output="""
# Contract fee: 0.00000166 BTC (0.00000672 BTC/kB)
# Refund fee:   0.00000297 BTC (0.00001017 BTC/kB)
#
# Contract (2MyUPdJFNzPLB64pd4N3rTrDhBv466DHM3S):
# 6382012088a82024856edde4429002952db9a47d55841f1365b7cc6006fa537b475353acc897678876a914762e80f7b2551a2739861a5c23143bbd95c061e667042e22475bb17576a914a8d41c962be0c756b25a5b087692f9dcc77d0ef16888ac
#
# Contract transaction (df83561db38cbd784ab5f53c124db544bdc74c75e636b693ebc22882d221ebea):
# 020000000001010eabecc71d0304a8f3fda29858b6380ff5f728aa519c3f914534c904b7c9c0270100000017160014344c91e759c0a38ea03ef04140c463d7f3bee735feffffff0250d412000000000017a914444e352f243bbbb64213f47a880040c2aa3c211b87283f23020000000017a914634e0d5fc9f1910a0890045debfd74a58e219c39870247304402206ef9ebdd9fe6707aa8d1a509f776d445927e60cdba50bf5c5d81b54835bf2598022007e445c6ee20e0c8b4533d74ff8fc789dd5993f2f14e425e70ffa13e0391a655012103c9b4e2d0719feda608e7818e666e0f1a1cd9ff9104b1b4491d5e2045a9e671bf00000000
#
# Refund transaction (0ffe5d9b0c7c2bbfc7793691f7c97c2ecbd413f29c191d7fd542524e49a82d93):
# 0200000001eaeb21d28228c2eb93b636e6754cc7bd44b54d123cf5b54a78bd8cb31d5683df00000000cf483045022100e9790898960369af436eab390b1dd18b5e3ead1c88ab7b6cd44a7c780d91904c02203c01759e91036a6eb3a416b23d7fe96944117c321cf298f5ac6358a7413b8d6d01210269cf7bc32dd71da4189c7473682a8b4b88a68b94b434b01a77d3553ec87d7962004c616382012088a82024856edde4429002952db9a47d55841f1365b7cc6006fa537b475353acc897678876a914762e80f7b2551a2739861a5c23143bbd95c061e667042e22475bb17576a914a8d41c962be0c756b25a5b087692f9dcc77d0ef16888ac000000000127d31200000000001976a914e10b245915601cc3b6b677d66660b7e228aa71ca88ac2e22475b
# """

        return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="initiate", logger=self.logger, test_output=test_output)



    def auditcontract(self, output_id, recipient_addr, secret_hash, amount, daemon_address=None):
        """
        Audit contract after the participant executed the participate step

        @param output_id: Output ID i.e the transaction id of the published contract from the participate step
        @param recipient_addr: Address of the recipient of the contract
        @param secret_hash: Hash of the secret
        @param amount: Amount of funds sent by the participant in the contract
        @param daemon_address: Which host/port to communicate with (i.e. the host/port tfchaind is listening on)
        """
        daemon_address = daemon_address or os.environ.get('TFT_DAEMON_ADDRESS', DEFAULT_TFT_DAEMON_ADDRESS)
        cmd = 'tfchainc -a {} atomicswap -y --encoding json auditcontract {} --receiver {} --secrethash {} --amount {}'.format(daemon_address, output_id, recipient_addr, secret_hash, amount)
        self._prefab.core.run(cmd, showout=False)



    def redeem(self, output_id, secret, daemon_address=None):
        """
        Redeems the amount of the contract

        @param output_id: Transaction ID of the participate step
        @param secret: Secret that was generated during the first initiate step

        @returns: @returns: A dictionary with the following format {'transaction_id': <>}
        """
        daemon_address = daemon_address or os.environ.get('TFT_DAEMON_ADDRESS', DEFAULT_TFT_DAEMON_ADDRESS)
        cmd = 'tfchainc -a {} atomicswap redeem {} {} -y --encoding json '.format(daemon_address, output_id, secret)
        _, out, _ = self._prefab.core.run(cmd, showout=False)
        out = json.loads(out)
        return {
            'transaction_id': out['transactionid'],
            }


    def refund(self, contract, contract_transaction, rpcuser=None, rpcpass=None, addr=None):
        """
        Refunds an atomicswap contract
        """
        rpcuser = rpcuser or os.environ.get('BTC_RPC_USER', DEFAULT_BTC_RPC_USER)
        rpcpass = rpcpass or os.environ.get('BTC_RPC_PASS', DEFAULT_BTC_RPC_PASS)
        addr = addr or os.environ.get('BTC_RPC_ADDRESS', DEFAULT_BTC_RPC_ADDRESS)
        cmd = 'btcatomicswap{} --rpcuser={} --rpcpass={} -s {} --force-yes refund {} {}'.format(' --testnet' if self._testnet else '',
                rpcuser, rpcpass, addr, contract, contract_transaction)
        self._prefab.core.run(cmd, showout=False)




class Participant(JSBASE):
    """
    Participant class
    """
    def __init__(self, prefab, initiator_address, amount, testnet):
        """
        Initializes a participant
        """
        self._prefab = prefab
        self._initiator_address = initiator_address
        self._amount = amount
        self._testnet = testnet
        JSBASE.__init__(self)


class TFTParticipant(Participant):
    """
    TFT Participant class
    """
    TFT_TESTNET_EXPLORER_URL = 'https://explorer.testnet.threefoldtoken.com'
    TFT_EXPLORER_URL = 'https://explorer.threefoldtoken.com/'
    TFT_MIN_CONFIRMATION_HEIGHT = 5


    def wait_for_confirmations(self, transaction_id, height_difference=None):
        """
        Waits until the transaction have been confirmed

        @param transaction_id: ID of the transaction to check
        @param height_difference: Minimum height difference between the transaction height and the current height of the chain to consider the transaction confirmed
        """
        if height_difference is None:
            height_difference = int(os.environ.get('TFT_MIN_CONFIRMATION_HEIGHT', self.TFT_MIN_CONFIRMATION_HEIGHT))
            # height_difference = self.TFT_MIN_CONFIRMATION_HEIGHT
        self.logger.info("Waiting for transaction {} to have at least {} height difference".format(transaction_id, height_difference))
        txn_info = self._get_txn_info(transaction_id=transaction_id)
        if txn_info['unconfirmed'] == True:
            self.logger.debug("Transaction with id {} is unconfirmed. Waiting until its confirmed...".format(transaction_id))
        while txn_info['unconfirmed'] == True:
            time.sleep(10)
            txn_info = self._get_txn_info(transaction_id=transaction_id)

        if txn_info['transactions']:
            txn_height = txn_info['transactions'][0]['height']
        elif txn_info['transaction'].get('height', None) is not None:
            txn_height = txn_info['transaction']['height']
        else:
            raise RuntimeError("Failed to retrieve transaction height for transaction {}".format(transaction_id ))
        current_height_difference = self.get_current_chain_height() - txn_height
        while current_height_difference < height_difference:
            time.sleep(20)
            current_height_difference = self.get_current_chain_height() - txn_height


    def get_current_chain_height(self):
        """
        Retrieves the current chain height
        """
        result = None
        url = '{}/explorer'.format(self.TFT_TESTNET_EXPLORER_URL if self._testnet else self.TFT_EXPLORER_URL)
        headers = {'user-agent': 'Rivine-Agent'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            msg = 'Failed to get current chain height. {}'.format(response.text)
            raise RuntimeError(msg)
        else:
            result = response.json().get('height', None)
            if result is not None:
                result = int(result)
        return result


    def _get_txn_info(self, transaction_id):
        """
        Retrieves details about a transaction

        @param transaction_id: Transaction to check
        """
        result = None
        timeout = 5 * 60
        url = '{}/explorer/hashes/{}'.format(self.TFT_TESTNET_EXPLORER_URL if self._testnet else self.TFT_EXPLORER_URL, transaction_id)
        headers = {'user-agent': 'Rivine-Agent'}
        response = requests.get(url, headers=headers)
        while timeout > 0:
            if response.status_code != 200:
                time.sleep(20)
                timeout -= 20
                response = requests.get(url, headers=headers)
            else:
                result = response.json()
                break
        if result is None:
            raise RuntimeError("Failed to get transaction details for {}".format(transaction_id))
        return result


    def auditcontract(self, contract, contract_txn, addr=None):
        """
        Audit an atomicswap transaction and retieve the output data

        @param contract: Contract produced from the initiate step of the initiator
        @param contract_txn: Contract transactoin value produced frmo the initiate step of the initiator

        @returns: a dictionary with the following format {'contract_addr': <>, 'contract_value': <>, 'recipient_addr', <>,
                                                            'refund_addr': <>, 'secret_hash': <>, 'remaining_locktime': <>}
        """
        addr = addr or os.environ.get('BTC_RPC_ADDRESS', DEFAULT_BTC_RPC_ADDRESS)
        cmd = 'btcatomicswap{} -s {} auditcontract {} {}'.format(' --testnet' if self._testnet else '',
                                                                    addr, contract, contract_txn)
        pattern = r'Contract\saddress:\s*(?P<contract_addr>\w+)\n*Contract\svalue:\s*(?P<contract_value>[\w.]+)\s+.*\n*Recipient\saddress:\s*(?P<recipient_addr>\w+)\n*.*refund\saddress:\s*(?P<refund_addr>\w+)\n*Secret\shash:\s*(?P<secret_hash>\w+)\n*.*\n*Locktime\sreached\sin\s*(?P<remaining_locktime>[\w.]+)\n*'
        test_output = None
#         test_output = """
# 0200000000010156901f407052d8c5185a54246e764d8304574aae13847c71ea5a2afb73d9e8e80000000017160014253584f1f207ff244c2d9dd10f2508b265f31395feffffff028a1be8020000000017a9144a0de4a6e8e5a52c7c249890a00c8bafa217510b8750d412000000000017a914f0a2561a9fd9de1ce4ee98f70de86ae3312f4873870247304402202761c014d6a3c69584d437153e0eb75f12e21f06ea267818bb7eca933ed892ef02201fd5ed6e24ae6fb684386a58cfcbbfde0ae1e16260bc52d3ce7e79a5e9ab98d80121031be3ad72917139bda0c3b4c3aa0e405772bb1b10168104604b4140eb7bf6338200000000
# Contract address:        2NFBadefP7PrqDWyyjfJZbvpJrs1Tx8BSke
# Contract value:          0.01234 BTC
# Recipient address:       n18MobJVWMLkWDTf8cku9DRAMTa86itr6D
# Author's refund address: muY1nb5swhfijRUovauF6uukbDLCyih1WY
#
# Secret hash: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8
#
# Locktime: 2018-05-22 12:31:39 +0000 UTC
# Locktime reached in 45h18m42s
# """

        return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="auditcontract", logger=self.logger, test_output=test_output)


    def initiate(self, daemon_address=None):
        """
        Initiate an atomicswap contract
        """
        daemon_address = daemon_address or os.environ.get('TFT_DAEMON_ADDRESS', DEFAULT_TFT_DAEMON_ADDRESS)
        cmd = "tfchainc -a {} atomicswap -y --encoding json initiate {} {}".format(daemon_address,
                                                                                self._initiator_address,
                                                                                self._amount)
        _, out, _ = self._prefab.core.run(cmd, showout=False)
        out = json.loads(out)
        return {
            'contract_addr': out['contractid'],
            'contract_value': int(out['coins']) / HASTINGS_TFT_VALUE,
            'recipient_addr': out['contract']['receiver'],
            'secret': out['secret'],
            'secret_hash': out['contract']['hashedsecret'],
            'output_id': out['outputid'],
            'transaction_id': out['transactionid'],
        }


    def participate(self, secret_hash, daemon_address=None):
        """
        Execute participate on an atomicswap transaction

        @param secret_hash: The secret hash produced by the initiate step
        @returns: A dictionary of the format {'contract_addr': <>, 'contract_value': <>, 'recipient_addr', <>,
                                                            'secret_hash': <>,
                                                            'output_id': <>}
        """
        daemon_address = daemon_address or os.environ.get('TFT_DAEMON_ADDRESS', DEFAULT_TFT_DAEMON_ADDRESS)
        cmd = "tfchainc -a {} atomicswap -y --encoding json participate {} {} {}".format(daemon_address,
                                                                                self._initiator_address,
                                                                                self._amount, secret_hash)
        _, out, _ = self._prefab.core.run(cmd, showout=False)
        # out = """{"coins":"500000000","contract":{"sender":"012ffd03d1b4d39ba9df8294bb5135a0a69768494a54e4df0c0eb817309b6a7fba795e4ac1f4ff","receiver":"0108031a2111cec5427954fae23fdd6a0cc21d9ab91cf0e878af9d2bb0081e9c1246da7c1e2346","hashedsecret":"0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e","timelock":1530126270},"contractid":"02806e2cfa3aa87e2ea41d4c1f1bf8bf2b73d167eb3df610b7b364633426b8215e607e40db08b1","outputid":"e27bfac78c16e7690b5cb477f1602e0f6b074522d198d4733dd03d148cac4024","transactionid":"09bb77d6555488103f59709d27f0679fcf4d86dfa3ae77dbb06d976aeccc947e"}"""
        out = json.loads(out)
        return {
            'contract_addr': out['contractid'],
            'contract_value': int(out['coins']) / HASTINGS_TFT_VALUE,
            'recipient_addr': out['contract']['receiver'],
            'secret_hash': out['contract']['hashedsecret'],
            'output_id': out['outputid'],
            'transaction_id': out['transactionid'],
        }


    def redeem(self, contract, contract_txn, secret, rpcuser=None, rpcpass=None, addr=None):
        """
        Redeems a contract that has already redeemed by the initiator

        @param contract: The contract that was created during the initiate step
        @param contract_txn: The contract transaction that was created during the initiate step
        @param secret: Secret that was generated during the first initiate step

        @returns: A dictionary with the following format {'transaction_id': <>}
        """
        rpcuser = rpcuser or os.environ.get('BTC_RPC_USER', DEFAULT_BTC_RPC_USER)
        rpcpass = rpcpass or os.environ.get('BTC_RPC_PASS', DEFAULT_BTC_RPC_PASS)
        addr = addr or os.environ.get('BTC_RPC_ADDRESS', DEFAULT_BTC_RPC_ADDRESS)
        cmd = 'btcatomicswap{} -s {} --rpcuser={} --rpcpass={} --force-yes redeem {} {} {}'.format(' --testnet' if self._testnet else '', addr,
                                                                                             rpcuser , rpcpass, contract, contract_txn, secret)
        pattern = r'Published\sredeem\stransaction\s*\((?P<transaction_id>\w+)\)'
        test_output = None
#         test_output = """
# Redeem fee: 0.0000033 BTC (0.00001019 BTC/kB)
#
# Redeem transaction (ddd1040fd2f255a82aba54255d39b7c8ccc43393f99fa2871c1557da216bf802):
# 0200000001d82f1c4a209385a503dfe519ac050f14f98983e62406bb6e5203fc2c4d957da301000000ef473044022079e824f3accd97fc3ba2f67a7a02caf60a6edc3678397b1f8f9d6dc624edeca60220156d9cfba11f220cbe133a63ad5c5b1c06582c169ee8a91da6d94ee38ef2d409012103a7e0010af3def18b827d45ddafcbbffea1f49ce468bb1d91f043e8feb8daa72c2058febdffd0dd5c141d27c45d8fb1a962e2e9a4eb991fac2da0bca56bd99736ca514c616382012088a82029bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db88876a914d71c92b78069af7047d0a6c367be634aeb5ad6ac6704ab0d045bb17576a91499c51785eb8ed83a06e495aee769f687616cdd4f6888acffffffff0106d31200000000001976a914754aea4184341fe1779faac5557b16879709bdcd88acab0d045b
#
# Published redeem transaction (ddd1040fd2f255a82aba54255d39b7c8ccc43393f99fa2871c1557da216bf802)
# """
        return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="redeem", logger=self.logger, test_output=test_output)


    def refund(self, output_id, secret, daemon_address=None):
        """
        Refund an atomicswap contract
        """
        daemon_address = daemon_address or os.environ.get('TFT_DAEMON_ADDRESS', DEFAULT_TFT_DAEMON_ADDRESS)
        cmd = "tfchainc -a {} atomicswap -y --encoding json refund {} {}".format(daemon_address,
                                                                                output_id,
                                                                                secret)
        _, out, _ = self._prefab.core.run(cmd, showout=False)
        out = json.loads(out)
        return {
            'transaction_id': out['transactionid'],
        }
