"""
Modules for common utilites
"""
import re
import time
import string
import requests
from random import choice
from pyblake2 import blake2b
from requests.auth import HTTPBasicAuth

from JumpScale9 import j
from JumpScale9Lib.clients.blockchain.rivine import secrets
from JumpScale9Lib.clients.blockchain.rivine.encoding import binary
from JumpScale9Lib.clients.blockchain.rivine.errors import RESTAPIError, BackendError
from JumpScale9Lib.clients.blockchain.rivine.const import HASH_SIZE, MINER_PAYOUT_MATURITY_WINDOW, TIMELOCK_CONDITION_HEIGHT_LIMIT


DURATION_REGX_PATTERN = '^(?P<hours>\d*)h(?P<minutes>\d*)m(?P<seconds>\d*)s$'
DURATION_TEMPLATE = 'XXhXXmXXs'

logger = j.logger.get(__name__)

def hash(data, encoding_type=None):
    """
    Hashes the input binary data using the blake2b algorithm

    @param data: Input data to be hashed
    @param encoding_type: Type of the data to guide the binary encoding before hashing
    @returns: Hashed value of the input data
    """
    binary_data = binary.encode(data, type_=encoding_type)
    return blake2b(binary_data, digest_size=HASH_SIZE).digest()


def locktime_from_duration(duration):
    """
    Parses a duration string and return a locktime timestamp

    @param duration: A string represent a duration if the format of XXhXXmXXs and return a timestamp
    @returns: number of seconds represented by the duration string
    """
    if not duration:
        raise ValueError("Duration needs to be in the format {}".format(DURATION_TEMPLATE))
    match = re.search(DURATION_REGX_PATTERN, duration)
    if not match:
        raise ValueError("Duration needs to be in the format {}".format(DURATION_TEMPLATE))
    values = match.groupdict()
    result = 0
    if values['hours']:
        result += int(values['hours']) * 60 * 60
    if values['minutes']:
        result += int(values['minutes']) * 60
    if values['seconds']:
        result += int(values['seconds'])

    return int(result)


def get_secret(size):
    """
    Generate a random secert token

    @param size: The size of the secret token
    """
    # alphapet = string.ascii_letters + string.digits
    # result = []
    # for _ in range(size):
    #     result.append(choice(alphapet))
    # return ''.join(result)
    return secrets.token_bytes(nbytes=size)


def get_current_chain_height(rivine_explorer_address):
    """
    Retrieves the current chain height
    """
    result = None
    url = '{}/explorer'.format(rivine_explorer_address.strip('/'))
    headers = {'user-agent': 'Rivine-Agent'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        msg = 'Failed to get current chain height. {}'.format(response.text)
        logger.error(msg)
        raise RESTAPIError(msg)
    else:
        result = response.json().get('height', None)
        if result is not None:
            result = int(result)
    return result


def check_address(rivine_explorer_address, address, log_errors=True):
    """
    Check if an address is valid and return its details

    @param address: Address to check
    @param log_errors: If False, no logging will be executed

    @raises: @RESTAPIError if failed to check address
    """
    result = None
    url = '{}/explorer/hashes/{}'.format(rivine_explorer_address.strip('/'), address)
    headers = {'user-agent': 'Rivine-Agent'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        msg = "Failed to retrieve address information. {}".format(response.text.strip('\n'))
        if log_errors:
            logger.error(msg)
        raise RESTAPIError(msg)
    else:
        result = response.json()
    return result


def get_unconfirmed_transactions(rivine_explorer_address, format_inputs=False):
    """
    Retrieves the unconfirmed transaction from a remote node that runs the Transaction pool module

    @param format_inputs: If True, the output will be formated to get a list of the inputs parent ids

    # example output
            {'transactions': [{'version': 1,
       'data': {'coininputs': [{'parentid': '7616c88f452d6b22a3683bcbdfdf6ee3c32b63a810a8ac0d46a7403a33d4c06f',
          'fulfillment': {'type': 1,
           'data': {'publickey': 'ed25519:9413b12a6158f52fad6c39cc164054a9e7fbe5378892311f498eae56f80c068a',
            'signature': '34cee9bbc380deba2f52ccb20c2a47d4f6001fe66cfe7079d6b71367ea14544e89e69657201d0cc7b7b901324e64a7f4dce6ac6177536726cee576a0b74a8700'}}}],
        'coinoutputs': [{'value': '2000000000',
          'condition': {'type': 1,
           'data': {'unlockhash': '0112a7c1813746c5f6d5d496441d7a6a226984a3cc318021ee82b5695e4470f160c6ca61f66df2'}}},
         {'value': '3600000000',
          'condition': {'type': 1,
           'data': {'unlockhash': '012bdb563a4b3b630ddf32f1fde8d97466376a67c0bc9a278c2fa8c8bd760d4dcb4b9564cdea6f'}}}],
        'minerfees': ['100000000']}}]}
    """
    result = []
    url = "{}/transactionpool/transactions".format(rivine_explorer_address.strip('/'))
    headers = {'user-agent': 'Rivine-Agent'}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        msg = 'Failed to retrieve unconfirmed transactions. Error: {}'.format(res.text)
        logger.error(msg)
        raise BackendError(msg)
    transactions = res.json()['transactions']
    if transactions is None:
        transactions = []
    if format_inputs:
        for txn in transactions:
            result.extend([coininput['parentid'] for coininput in txn['data']['coininputs']])
        return result
    return transactions


def commit_transaction(rivine_explorer_address, rivine_explorer_api_password, transaction):
    """
    Commits a singed transaction to the chain

    @param transaction: Transaction object to be committed
    """
    data = transaction.json
    url = '{}/transactionpool/transactions'.format(rivine_explorer_address.strip('/'))
    headers = {'user-agent': 'Rivine-Agent'}
    auth = HTTPBasicAuth('', rivine_explorer_api_password)
    res = requests.post(url, headers=headers, auth=auth, json=data)
    if res.status_code != 200:
        msg = 'Faield to commit transaction to chain network.{}'.format(res.text)
        logger.error(msg)
        raise BackendError(msg)
    else:
        transaction.id = res.json()['transactionid']
        logger.info('Transaction committed successfully')
        return transaction.id


def get_unlockhash_from_output(output, address, current_height):
    """
    Retrieves unlockhash from coin output. This should handle different types of output conditions and transaction formats

    @param current_height: The current chain height
    """
    result = {
        'locked': [],
        'unlocked': []
    }
    # support both v0 and v1 tnx format
    if 'unlockhash' in output:
        # v0 transaction format
        result['unlocked'].append(output['unlockhash'])
    elif 'condition' in output:
        # v1 transaction format
        # check condition type
        if output['condition'].get('type') == 1:
            # unlockhash condition type
            result['unlocked'].append(output['condition']['data']['unlockhash'])
        elif output['condition'].get('type') == 3:
            # timelock condition, right now we only support timelock condition with internal unlockhash condition, and multisig condition
            locktime = output['condition']['data']['locktime']
            if locktime < TIMELOCK_CONDITION_HEIGHT_LIMIT:
                if output['condition']['data']['condition']['type'] == 1:
                    # locktime should be checked against the current chain height
                    if current_height > locktime:
                        result['unlocked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                elif output['condition']['data']['condition']['type'] == 4:
                    # locktime should be checked against the current chain height
                    if current_height > locktime:
                        result['unlocked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
            else:
                # locktime represent timestamp
                current_time = time.time()
                if output['condition']['data']['condition']['type'] == 1:
                    # locktime should be checked against the current time
                    if current_time > locktime:
                        result['unlocked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                elif output['condition']['data']['condition']['type'] == 4:
                    # locktime should be checked against the current time
                    if current_time > locktime:
                        result['unlocked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))

        elif output['condition'].get('type') == 4:
            result['unlocked'].extend(output['condition']['data']['unlockhashes'])

    return result


def collect_miner_fees(address, blocks, height):
    """
    Scan the bocks for miner fees and Collects the miner fees But only that have matured already

    @param address: address to collect miner fees for
    @param blocks: Blocks from an address
    @param height: The current chain height
    """
    result = {}
    if blocks is None:
        blocks = {}
    for block_info in blocks:
        if block_info.get('height', None) and block_info['height'] + MINER_PAYOUT_MATURITY_WINDOW >= height:
            logger.info('Ignoring miner payout that has not matured yet')
            continue
        # mineroutputs can exist in the dictionary but with value None
        mineroutputs = block_info.get('rawblock', {}).get('minerpayouts', [])
        if mineroutputs:
            for index, minerpayout in enumerate(mineroutputs):
                if minerpayout.get('unlockhash') == address:
                    logger.info('Found miner output with value {}'.format(minerpayout.get('value')))
                    result[block_info['minerpayoutids'][index]] = {
                        'value': minerpayout['value'],
                        'condition':{
                            'data': {
                                'unlockhash': address
                            }
                        }
                    }
    return result


def collect_transaction_outputs(current_height, address, transactions, unconfirmed_txs=None):
    """
    Collects transactions outputs

    @param current_height: The current chain height
    @param address: address to collect transactions outputs
    @param transactions: Details about the transactions
    @param unconfirmed_txs: List of unconfirmed transactions
    """
    result = {
        'locked': {},
        'unlocked': {}
    }
    if unconfirmed_txs is None:
        unconfirmed_txs = []
    for txn_info in transactions:
        # coinoutputs can exist in the dictionary but has the value None
        coinoutputs = txn_info.get('rawtransaction', {}).get('data', {}).get('coinoutputs', [])
        if coinoutputs:
            for index, utxo in enumerate(coinoutputs):
                condition_ulh = get_unlockhash_from_output(output=utxo, address=address, current_height=current_height)

                if address in condition_ulh['locked'] or address in condition_ulh['unlocked']:
                    logger.debug('Found transaction output for address {}'.format(address))
                    if txn_info['coinoutputids'][index] in unconfirmed_txs:
                        logger.warn("Transaction output is part of an unconfirmed tansaction. Ignoring it...")
                        continue
                    if address in condition_ulh['locked']:
                        result['locked'][txn_info['coinoutputids'][index]] = utxo
                    else:
                        result['unlocked'][txn_info['coinoutputids'][index]] = utxo
    return result


def remove_spent_inputs(unspent_coins_outputs, transactions):
    """
    Remvoes the already spent outputs

    @param transactions: Details about the transactions
    """
    for txn_info in transactions:
        # cointinputs can exist in the dict but have the value None
        coininputs = txn_info.get('rawtransaction', {}).get('data', {}).get('coininputs', [])
        if coininputs:
            for coin_input in coininputs:
                if coin_input.get('parentid') in unspent_coins_outputs:
                    logger.debug('Found a spent address {}'.format(coin_input.get('parentid')))
                    del unspent_coins_outputs[coin_input.get('parentid')]


def find_subset_sum(values, target):
    """
    Find a subset of the values that sums to the target number
    This implements a dynamic programming approach to the subset sum problem
    Implementation is taken from: https://github.com/saltycrane/subset-sum/blob/master/subsetsum/stackoverflow.py

    @param values: List of integers
    @param target: The sum that we need to find a subset to equal to it.
    """
    def g(v, w, S, memo):
        subset = []
        id_subset = []
        for i, (x, y) in enumerate(zip(v, w)):
            # Check if there is still a solution if we include v[i]
            if f(v, i + 1, S - x, memo) > 0:
                subset.append(x)
                id_subset.append(y)
                S -= x
        return subset, id_subset


    def f(v, i, S, memo):
        if i >= len(v):
            return 1 if S == 0 else 0
        if (i, S) not in memo:    # <-- Check if value has not been calculated.
            count = f(v, i + 1, S, memo)
            count += f(v, i + 1, S - v[i], memo)
            memo[(i, S)] = count  # <-- Memoize calculated result.
        return memo[(i, S)]       # <-- Return memoized value.

    memo = dict()
    result, _ = g(values, values, target, memo)
    return result
