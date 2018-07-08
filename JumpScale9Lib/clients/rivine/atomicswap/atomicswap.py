"""
This module add the support of atomicswaps to the rivine light weight client
"""
import time
import hashlib
from JumpScale9 import j
from JumpScale9Lib.clients.rivine import utils
from JumpScale9Lib.clients.rivine.const import HASTINGS_TFT_VALUE, ATOMICSWAP_SECRET_SIZE
from JumpScale9Lib.clients.rivine.types.transaction import TransactionFactory, DEFAULT_TRANSACTION_VERSION

logger = j.logger.get(__name__)

class AtomicSwapManager:
    """
    A manager class to expose high level APIs for atomicswap operations
    """

    def __init__(self, wallet):
        """
        Initializes a new AtomicSwapManager instance

        @param wallet: An instance of RivineWallet that will be used to create tansactions
        """
        self._wallet = wallet


    def initiate(self, participant_address, amount, duration='48h0m0s', refund_address=None):
        """
        Create an atomic swap contract as initiator

        @param participant_address: Address of the participant (unlockhash) to send the money to.
        @param amount: The mount of TF tokens to use for the atomicswap contract
        @param duration: The duration of the atomic swap contract, the amount of time the participator has to collect (default 48h0m0s)
        @param refund_address: Address to receive the funds back if transaction is not compeleted (AUTO selected from the wallet if not provided)
        """

        if refund_address is None:
            refund_address = self._wallet.generate_address()
        # convert amount to hastings
        actuall_amount = amount * HASTINGS_TFT_VALUE
        if type(duration) == int:
            locktime = duration
        else:
            locktime = int(time.time()) + utils.locktime_from_duration(duration=duration)
        input_results, used_addresses, minerfee, remainder = self._wallet._get_inputs(amount=actuall_amount)
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)
        for input_result in input_results:
            transaction.add_coin_input(**input_result)

        # generate a secret
        secret = utils.get_secret(size=ATOMICSWAP_SECRET_SIZE)
        # hash the secret
        hashed_secret = hashlib.sha256(bytearray(secret, encoding='utf-8')).digest().hex()
        # TODO: Remove this only for testing
        # hashed_secret = '8d886f9981d77842cc26562ca330e034bf34229a27a57767b34ba1083bc8e1da'

        ats_coin_output = transaction.add_atomicswap_output(value=actuall_amount,recipient=participant_address,
                                         locktime=locktime, refund_address=refund_address,
                                         hashed_secret=hashed_secret)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            for address in self._wallet._keys.keys():
                if address in used_addresses.values():
                    continue
                transaction.add_coin_output(value=remainder, recipient=address)
                break

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        # sign the transaction
        self._wallet._sign_transaction(transaction)

        # commit transaction
        txn_id = self._wallet._commit_transaction(transaction)

        # retrieve the info from the transaction
        ats_output_id = None
        txn_info = self._wallet._check_address(txn_id)
        coinoutputs = txn_info.get("transaction", {}).get('rawtransaction', {}).get('data', {}).get('coinoutputs', [])
        if coinoutputs:
            for index, coin_output in enumerate(coinoutputs):
                if coin_output == ats_coin_output.json:
                    ats_output_id = txn_info['transaction']['coinoutputids'][index]

        return {
            'transaction_id': txn_id,
            'output_id': ats_output_id,
            'secret': secret,
            'hashed_secret': hashed_secret,
            'amount': amount
        }
