from js9 import j

participant_address = '01cbbad52e911ebfa7e52153b3517197129ba6b7ae697ce3b25c18ed5d6f2e8da36e40008f98f6'
refund_address = '0167fa42318444eb27a6c592bc0e3e38db65de0c5b5eeb0f7bb7ee055045bb671f90fe89406f33'
btc_address = 'mrHqjq3t7imHTFGAn84tbvL1nVeSff6B9z'
btc_node_address = 'localhost:2200'
tft_node_address = 'localhost:2222'
amount = 2
wallet = j.clients.rivine.get('mytestwallet').wallet
# duration=1531059743
try:
    initiator = j.tools.atomicswap.get_btc_initiator(btc_node_address, amount=0.01234, recipient_address=btc_address,
                                                    testnet=True)
    participant = j.tools.atomicswap.get_tft_participant(tft_node_address, amount=amount, recipient_address=participant_address,
                                                    testnet=True)
    initiate_result = participant.initiate()
    # contract = wallet.atomicswap.initiate(participant_address=participant_address, amount=amount,
    #                                     duration='48h0m0s', refund_address=refund_address)
    # print(contract)
    # participate_result = initiator.participate(secret_hash=contract['hashed_secret'])

    # initiat_result = initator.initiate()
    # print(initiat_result)
    # contract = wallet.atomicswap.participate(initiator_address=participant_address, amount=amount, hashed_secret=initiat_result['secret_hash'],
    #                                     duration='24h0m0s', refund_address=refund_address)
    # print(contract)
    # initiator.auditcontract(output_id=contract['output_id'], recipient_addr=participant_address,
    #                         secret_hash=contract['hashed_secret'], amount=contract['amount'],
    #                         daemon_address='localhost:23130')
    # initiator.redeem(output_id=contract['output_id'], secret=initiat_result['secret'], daemon_address='localhost:23130')

    # wallet.atomicswap.refund(output_id='a5f2962e9d96e558fe9bad763a271ff25bdba6d2a98124a68d29d184a81fade5')
except Exception:
    raise
    print("Error")
finally:
    import IPython
    IPython.embed()
