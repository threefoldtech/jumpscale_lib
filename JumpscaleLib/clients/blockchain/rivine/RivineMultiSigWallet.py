"""
Module that defines required classes for Mulitsignature wallets
"""
import json

from JumpScale9 import j
from JumpScale9Lib.clients.blockchain.rivine import const
from JumpScale9Lib.clients.blockchain.rivine import utils
from JumpScale9Lib.clients.blockchain.rivine.merkletree import Tree
from JumpScale9Lib.clients.blockchain.rivine.encoding import binary
from JumpScale9Lib.clients.blockchain.rivine.errors import RESTAPIError, InsufficientWalletFundsError
from JumpScale9Lib.clients.blockchain.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_MULTISIG
from JumpScale9Lib.clients.blockchain.rivine.types.transaction import TransactionFactory, DEFAULT_TRANSACTION_VERSION

logger = j.logger.get(__name__)

class RivineMultiSignatureWallet:
    """
    RivineMultiSignatureWallet class
    """

    def __init__(self, cosigners, required_sig, bc_network, bc_network_password, minerfee=100000000, client=None):
        """
        Initializes a new RivineMultiSignatureWallet

        @param cosigners: List of lists, the length of outer list indicates the number of cosigners and the length of the inner lists indicates the number of unlockhashes
        @param required_sig: Minimum number of signatures required for the output sent to any of the Multisig addresses to be spent
        @param bc_network: Blockchain network to use.
        @param bc_network_password: Password to send to the explorer node when posting requests.
        @param minerfee: Amount of hastings that should be minerfee (default to 0.1 TFT)
        @param client: Name of the insance of the j.clients.rivine that is used to create the wallet
        """
        self._cosigners = cosigners
        self._required_sig = required_sig
        self._bc_network = bc_network
        self._bc_network_password = bc_network_password
        self._minerfee = minerfee
        self._client = client
        self._nr_of_cosigners = len(self._cosigners)
        self._unspent_outputs = {
            'locked': {},
            'unlocked': {}
        }
        self._address_ulhs_map = {}


    @property
    def current_balance(self):
        """
        Retrieves the current balance of the wallet
        """
        self._get_unspent_outputs()
        result = {
            'locked': 0,
            'unlocked': 0
        }
        for _, output_info in self._unspent_outputs['locked'].items():
            result['locked'] += int(output_info['value'])

        for _, output_info in self._unspent_outputs['unlocked'].items():
            result['unlocked'] += int(output_info['value'])
        result['locked'] /= const.HASTINGS_TFT_VALUE
        result['unlocked'] /= const.HASTINGS_TFT_VALUE

        return result


    @property
    def addresses(self):
        """
        Generates a list of multisig addresses
        """
        if not self._address_ulhs_map and self._nr_of_cosigners > 0:
            for index in range(len(self._cosigners[0])):
                ulhs = []
                for sub_index in range(self._nr_of_cosigners):
                    ulhs.append(self._cosigners[sub_index][index])
                self._address_ulhs_map[self._generate_multisig_address(ulhs)] = ulhs

        return [address for address in self._address_ulhs_map.keys()]


    def _generate_multisig_address(self, ulhs):
        """
        Generates a multisig address
        """
        mtree = Tree(hash_func=utils.hash)
        mtree.push(binary.encode(self._nr_of_cosigners))
        # make sure that regardless of the order of the unlockhashes, we sort them so that we always
        # produce the same multisig address
        for ulh in sorted(ulhs):
            mtree.push(binary.encode(UnlockHash.from_string(ulh)))

        mtree.push(binary.encode(self._required_sig))
        address_hash = mtree.root()
        ulh = UnlockHash(unlock_type=UNLOCK_TYPE_MULTISIG, hash=address_hash)
        return str(ulh)

    def _collect_transaction_outputs(self, current_height, address, ulhs, transactions, unconfirmed_txs):
        """
        Collects transactions outputs
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
                    condition_ulh = utils.get_unlockhash_from_output(output=utxo, address=address, current_height=current_height)

                    if set(ulhs).intersection(set(condition_ulh['locked'])) or set(ulhs).intersection(set(condition_ulh['unlocked'])):
                        logger.debug('Found transaction output for address {}'.format(address))
                        if txn_info['coinoutputids'][index] in unconfirmed_txs:
                            logger.warn("Transaction output is part of an unconfirmed tansaction. Ignoring it...")
                            continue
                        if set(ulhs).intersection(set(condition_ulh['locked'])):
                            result['locked'][txn_info['coinoutputids'][index]] = utxo
                        else:
                            result['unlocked'][txn_info['coinoutputids'][index]] = utxo
        return result

    def _get_unspent_outputs(self):
        """
        Retrieves the unpent outputs for this wallets addresses
        """
        addresses_info = {}
        current_chain_height = utils.get_current_chain_height(self._bc_network)
        unconfirmed_txs = utils.get_unconfirmed_transactions(self._bc_network, format_inputs=True)
        logger.info('Current chain height is: {}'.format(current_chain_height))
        for address in self.addresses:
            try:
                address_info = utils.check_address(self._bc_network, address, log_errors=False)
            except RESTAPIError:
                pass
            else:
                if address_info.get('hashtype', None) != const.UNLOCKHASH_TYPE:
                    raise BackendError('Address is not recognized as an unblock hash')
                addresses_info[address] = address_info
                minerfees_outputs = utils.collect_miner_fees(address=address,
                                                            blocks=address_info.get('blocks',{}),
                                                            height=current_chain_height)
                self._unspent_outputs['unlocked'].update(minerfees_outputs)
                transactions = address_info.get('transactions', {})
                txn_outputs = self._collect_transaction_outputs(current_height=current_chain_height,
                                                            address=address,
                                                            ulhs=self._address_ulhs_map[address],
                                                            transactions=transactions,
                                                            unconfirmed_txs=unconfirmed_txs)
                self._unspent_outputs.update(txn_outputs)
        # remove spent inputs after collection all the inputs
        for address, address_info in addresses_info.items():
            utils.remove_spent_inputs(unspent_coins_outputs=self._unspent_outputs['unlocked'], transactions=address_info.get('transactions', {}))

    def _get_inputs(self, amount, minerfee=None):
        """
        Retrieves a list of outputs that can be used as input that match the required amount
        """
        if minerfee is None:
            minerfee = self._minerfee
        wallet_fund = int(self.current_balance['unlocked'] * const.HASTINGS_TFT_VALUE)
        required_funds = amount + minerfee
        if required_funds > wallet_fund:
            raise InsufficientWalletFundsError('No sufficient funds to make the transaction')

        result = []
        value_output_id_map = {}
        output_values = []
        # create a map with the value and the corresponding input ids list
        # also create a flat list of the values (to allow duplicate values in the list)
        for output_id, unspent_coin_output in self._unspent_outputs['unlocked'].items():
            value = int(unspent_coin_output['value'])
            if value not in value_output_id_map:
                value_output_id_map[value] = []
            value_output_id_map[value].append(output_id)
            output_values.append(value)
        result_values = utils.find_subset_sum(output_values, required_funds)

        # once we got the values that sum up to the required funds, we retrieve the input ids from the map
        if not result_values:
            raise RuntimeError("Cannot match unspent outputs values to the the sum of (amount + minerfee)={}".format(required_funds))

        for result_value in result_values:
            result.append(value_output_id_map[result_value].pop())

        return result



    def create_transaction(self, amount, recipient, minerfee=None, data=None, locktime=None):
        """
        Create a transaction spending one/more multisignature output(s)

        @param amount: The amount needed to be transfered in TF Tokens
        @param recipient: Address of the recipient.
        @param minerfee: The minerfee for this transaction in TF Tokens
        @param data: Custom data to add to the transaction record
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        if minerfee is None:
            minerfee = self._minerfee
        else:
            minerfee = minerfee * const.HASTINGS_TFT_VALUE
        amount = int(amount * const.HASTINGS_TFT_VALUE)
        inputs = self._get_inputs(amount=amount,
                                  minerfee=minerfee)

        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)

        if data is not None:
            transaction.add_data(data)
        transaction.add_minerfee(minerfee)

        for input in inputs:
            # create an input with multisig fulfillment
            transaction.add_multisig_input(parent_id=input)

        transaction.add_coin_output(value=amount, recipient=recipient, locktime=locktime)

        return json.dumps(transaction.json)
