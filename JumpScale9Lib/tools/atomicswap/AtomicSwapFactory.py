"""
Factory Module for atomic swap
"""
from js9 import j
import re
import requests
import time
import json



JSBASE = j.application.jsbase_get_class()

SUPPORTED_CURRENCIES = ['BTC', 'TFT']
DEFAULT_LOCKTIME_THRESHOLD = 25
HASTINGS_TFT_VALUE = 1000000000.0


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
        self.logger.info("Executing paricipate operation")
        participate_result = participant.participate(secret_hash=initiate_result['secret_hash'])

        participant.wait_for_confirmations(transaction_id=participate_result['output_id'])

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
    BTC_TESTNET_EXPLORER_URL = 'https://api.blockcypher.com/v1/btc/test3/txs'
    BTC_EXPLORER_URl = 'https://api.blockcypher.com/v1/btc/main/txs'
    BTC_MIN_CONFIRMATIONS = 6


    def wait_for_confirmations(self, transaction_id, nr_of_confirmations=None):
        """
        Waits until the transaction have specific number of confirmations

        @param transaction_id: ID of the transaction to check
        @param nr_of_confirmations: Number of confirmations to wait for
        """
        if nr_of_confirmations is None:
            nr_of_confirmations = self.BTC_MIN_CONFIRMATIONS
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



    def initiate(self, rpcuser='user', rpcpass='pass', addr='localhost:8332'):
        """
        Initiate an atomic swap
        btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 --force-yes initiate n18MobJVWMLkWDTf8cku9DRAMTa86itr6D 0.01234
        """
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



    def auditcontract(self, output_id, recipient_addr, secret_hash, amount):
        """
        Audit contract after the participant executed the participate step

        @param output_id: Output ID i.e the transaction id of the published contract from the participate step
        @param recipient_addr: Address of the recipient of the contract
        @param secret_hash: Hash of the secret
        @param amount: Amount of funds sent by the participant in the contract
        """
        cmd = 'tfchainc atomicswap -y --encoding json auditcontract {} --receiver {} --secrethash {} --amount {}'.format(output_id, recipient_addr, secret_hash, amount)
        self._prefab.core.run(cmd)
        # pattern = r'Contract\saddress:\s*(?P<contract_addr>\w+)\n*Recipient\saddress:\s*(?P<recipient_addr>\w+)\n*Refund\saddress:\s*(?P<refund_addr>\w+)\n*Hashed\sSecret:\s*(?P<secret_hash>\w+)\n*Locktime:\s*(?P<locktime>\w+)\s*.*\n*Locktime\sreached\sin:\s*(?P<remaining_locktime>[\w.]+)\n*'
        # test_output = None
#         test_output = """
# Given unlock hash matches the given contract information :)
#
# Contract address: 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5
# Recipient address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d
# Refund address: 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320
#
# Hashed Secret: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8
#
# Locktime: 1526917093 (2018-05-21 15:38:13 +0000 UTC)
# Locktime reached in: 23h22m31.925443992s
#
# This was a quick check only, whether it has been spend already or not is unclear.
# You can do a complete/thorough check when auditing using the output ID instead.
# """
        # return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="audit", logger=self.logger, test_output=test_output)



    def redeem(self, output_id, secret):
        """
        Redeems the amount of the contract

        @param output_id: Transaction ID of the participate step
        @param secret: Secret that was generated during the first initiate step

        @returns: @returns: A dictionary with the following format {'transaction_id': <>}
        """
        cmd = 'tfchainc atomicswap redeem {} {} -y --encoding json '.format(output_id, secret)
        _, out, _ = self._prefab.core.run(cmd)
        out = json.loads(out)
        return {
            'transaction_id': out['transactionid'],
            }
        # pattern = r'Contract\saddress:\s*(?P<contract_addr>\w+)\n*Recipient\saddress:\s*(?P<recipient_addr>\w+)\n*Refund\saddress:\s*(?P<refund_addr>\w+)\n*Hashed\sSecret:\s*(?P<secret_hash>\w+)\n*Locktime:\s*(?P<locktime>\w+)\s*.*\n*Locktime\sreached\sin:\s*(?P<remaining_locktime>[\w.]+)\n*.*\n*Transaction\sID:\s*(?P<transaction_id>\w+)'
        # test_output = None
#         test_output = """
# An unspend atomic swap contract could be found for the given outputID,
# and the given contract information matches the found contract's information, all good! :)
#
# Contract address: 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5
# Recipient address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d
# Refund address: 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320
#
# Hashed Secret: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8
#
# Locktime: 1526917093 (2018-05-21 15:38:13 +0000 UTC)
# Locktime reached in: 22h17m17.217868994s
#
#
# Published atomic swap claim transaction!
# Transaction ID: e506a3e3b7883c79df52f751bb3cd4a0b1bed9a670a1eb9e612fee891bb58ac6
# >   NOTE that this does NOT mean for 100% you'll have the money!
# > Due to potential forks, double spending, and any other possible issues your
# > claim might be declined by the network. Please check the network
# > (e.g. using a public explorer node or your own full node) to ensure
# > your payment went through. If not, try to audit the contract (again).
# """

        # return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="redeem", logger=self.logger, test_output=test_output)


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
            height_difference = self.TFT_MIN_CONFIRMATION_HEIGHT
        self.logger.info("Waiting for transaction {} to have at least {} height difference".format(transaction_id, height_difference))
        txn_info = self._get_txn_info(transaction_id=transaction_id)
        if txn_info['transactions']:
            txn_height = txn_info['transactions'][0]['height']
        elif txn_info['transaction'].get('height'):
            txn_height = txn_info['transaction']['height']
        else:
            raise RuntimeError("Failed to retrieve transaction height for transaction {}".format(transaction_id ))
        current_height_difference = self._get_current_chain_height() - txn_height
        while current_height_difference < height_difference:
            time.sleep(20)
            current_height_difference = self._get_current_chain_height() - txn_height


    def _get_current_chain_height(self):
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


    def auditcontract(self, contract, contract_txn, addr='localhost:8332'):
        """
        Audit an atomicswap transaction and retieve the output data

        @param contract: Contract produced from the initiate step of the initiator
        @param contract_txn: Contract transactoin value produced frmo the initiate step of the initiator

        @returns: a dictionary with the following format {'contract_addr': <>, 'contract_value': <>, 'recipient_addr', <>,
                                                            'refund_addr': <>, 'secret_hash': <>, 'remaining_locktime': <>}
        """
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


    def participate(self, secret_hash):
        """
        Execute participate on an atomicswap transaction
        tfchainc atomicswap participate 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d .5 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8

        @param secret_hash: The secret hash produced by the initiate step
        @returns: A dictionary of the format {'contract_addr': <>, 'contract_value': <>, 'recipient_addr', <>,
                                                            'secret_hash': <>,
                                                            'output_id': <>}
        """
        cmd = "tfchainc atomicswap -y --encoding json participate {} {} {}".format(self._initiator_address,
                                                                                            self._amount, secret_hash)
        _, out, _ = self._prefab.core.run(cmd)
        out = """{"coins":"500000000","contract":{"sender":"012ffd03d1b4d39ba9df8294bb5135a0a69768494a54e4df0c0eb817309b6a7fba795e4ac1f4ff","receiver":"0108031a2111cec5427954fae23fdd6a0cc21d9ab91cf0e878af9d2bb0081e9c1246da7c1e2346","hashedsecret":"0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e","timelock":1530126270},"contractid":"02806e2cfa3aa87e2ea41d4c1f1bf8bf2b73d167eb3df610b7b364633426b8215e607e40db08b1","outputid":"e27bfac78c16e7690b5cb477f1602e0f6b074522d198d4733dd03d148cac4024","transactionid":"09bb77d6555488103f59709d27f0679fcf4d86dfa3ae77dbb06d976aeccc947e"}"""
        out = json.loads(out)
        return {
            'contract_addr': out['contractid'],
            'contract_value': int(out['coins']) / HASTINGS_TFT_VALUE,
            'recipient_addr': out['contract']['receiver'],
            'secret_hash': out['contract']['hashedsecret'],
            'output_id': out['outputid']
        }
        # pattern = r'Contract\saddress:\s*(?P<contract_addr>\w+)\n*Contract\svalue:\s*(?P<contract_value>[\w.]+)\s+.*\n*Recipient\saddress:\s*(?P<recipient_addr>\w+)\n*Refund\saddress:\s*(?P<refund_addr>\w+)\n*Hashed\sSecret:\s*(?P<secret_hash>\w+)\n*Locktime:\s*(?P<locktime>\w+)\s*.*\n*Locktime\sreached\sin:\s*(?P<remaining_locktime>[\w.]+)\n*.*\n*OutputID:\s+(?P<output_id>\w+)'
        # test_output = None
#         test_output = """
# Contract address: 028761224dfb7fd4a34ed29e65852500ada0e2b54e017200cd97d1626af2c4544bb055199553a5
# Contract value: 0.5 TFT
# Recipient address: 01c0f0bb61e95dd7e1e414b78f08117c5dae8327114979fecc0d07542ab9d047515066ae19594d
# Refund address: 015a88c1bffaf989e10d9b9dd4262090a1185b8a1c159e93101be09a86ccab988b0b7a43c61320
#
# Hashed Secret: 29bc7db3f1809b2bbd2091e5225d7dc2660826a78b8b734b8783cf2ae3830db8
#
# Locktime: 1526917093 (2018-05-21 17:38:13 +0200 CEST)
# Locktime reached in: 23h59m59.241241198s
#
# published contract transaction
# OutputID: dafed64af281bccf03fda2da4814281251d13d9bfb3aea95f3e505b160b6efe5
# """

        # return _execute_and_extract(prefab=self._prefab, cmd=cmd, regex=pattern, cmd_name="participate", logger=self.logger, test_output=test_output)


    def redeem(self, contract, contract_txn, secret, rpcuser='user', rpcpass='pass', addr='localhost:8332'):
        """
        Redeems a contract that has already redeemed by the initiator

        @param contract: The contract that was created during the initiate step
        @param contract_txn: The contract transaction that was created during the initiate step
        @param secret: Secret that was generated during the first initiate step

        @returns: A dictionary with the following format {'transaction_id': <>}
        """
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
