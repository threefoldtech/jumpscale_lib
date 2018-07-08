from js9 import j

participant_address = '016ae49755d320472b29b76bf90dfa56a5725bee0ac666a23482fb6b6703c594640afa5fa41eee'
refund_address = '0167fa42318444eb27a6c592bc0e3e38db65de0c5b5eeb0f7bb7ee055045bb671f90fe89406f33'
amount = 2
wallet = j.clients.rivine.get('mytestwallet').wallet
# duration=1531059743
try:
    txn = wallet.atomicswap.initiate(participant_address=participant_address, amount=amount, refund_address=refund_address)
    # co = txn.coins_outputs[0]
    # co._condition._sender = '0167c0ae9ca3b7cc8005e34af127a1948b242a97627699b75d1ca798bffd3f3af7051f055eae27'
    # co._condition._hashed_secret = '4b9b877878c7fd3c4151e868157b1507e1a2a6b907dd8b02092a68fd0b7e8cf5'
    # co._condition._locktime = 1531059743
    # print(co._condition.binary.hex())
    # import json
    # print(json.dumps(txn.json))
    print(txn)
except Exception:
    raise
    print("Error")
finally:
    import IPython
    IPython.embed()
