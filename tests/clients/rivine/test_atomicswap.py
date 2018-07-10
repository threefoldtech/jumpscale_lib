from js9 import j

participant_address = '01b6c585e9421143c67af0252b25f32156784b4dc9e935c5c74653aa0259b440a22488c0c3c365'
refund_address = '0167fa42318444eb27a6c592bc0e3e38db65de0c5b5eeb0f7bb7ee055045bb671f90fe89406f33'
btc_address = 'mqWdBhnYqoeNLaV9b638Ha4hz4n43iY5rZ'
btc_node_address = 'localhost:2200'
amount = 2
wallet = j.clients.rivine.get('mytestwallet').wallet
# duration=1531059743
try:
    initiator = j.tools.atomicswap.get_btc_initiator(btc_node_address, amount=0.01234, recipient_address=btc_address,
                                                    testnet=True)
    initiat_result = initator.initiate()
    print(initiat_result)
    contract = wallet.atomicswap.participate(initiator_address=participant_address, amount=amount, hashed_secret=initiat_result['secret_hash'],
                                        duration='24h0m0s', refund_address=refund_address)
    print(contract)
    initiator.auditcontract(output_id=contract['output_id'], recipient_addr=participant_address,
                            secret_hash=contract['hashed_secret'], amount=contract['amount'],
                            daemon_address='localhost:23130')
    initiator.redeem(output_id=contract['output_id'], secret=initiat_result['secret'], daemon_address='localhost:23130')

    # co = txn.coins_outputs[0]
    # co._condition._sender = '0167c0ae9ca3b7cc8005e34af127a1948b242a97627699b75d1ca798bffd3f3af7051f055eae27'
    # co._condition._hashed_secret = '4b9b877878c7fd3c4151e868157b1507e1a2a6b907dd8b02092a68fd0b7e8cf5'
    # co._condition._locktime = 1531059743
    # print(co._condition.binary.hex())
    # import json
    # print(json.dumps(txn.json))
    # print(txn)
    # {'amount': 2, 'secret': 'd2866f389eb80c0ef08ffe1d0e0bbd70b3518981220d822a4ec99f2f62622a66', 'hashed_secret': 'ac078892496b175c321860da525c7b5126db06fd6fa34f3c76db10ade0e82325', 'transaction_id': 'ebc6eb17769adca601edb7280002a6907fd918e78e471bb952e8ffb053cbde2f', 'output_id': '09a72e3d42365f8ddf3ec65f2b01c4930831f2c4da7c88db42e69894f319e54b'}
    # wallet.atomicswap.refund(output_id='a5f2962e9d96e558fe9bad763a271ff25bdba6d2a98124a68d29d184a81fade5')
except Exception:
    raise
    print("Error")
finally:
    import IPython
    IPython.embed()
