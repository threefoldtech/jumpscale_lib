"""
Test module for atomicswap
"""
import re
from js9 import j
import os
from JumpScale9Lib.tools.atomicswap.AtomicSwapFactory import BTCInitiator, TFTParticipant

os.environ.setdefault('BTC_MIN_CONFIRMATIONS', '1')
os.environ.setdefault('TFT_MIN_CONFIRMATION_HEIGHT', '2')

participant_address = 'mhv5Tve23BkVD6a8tpWKFxzWkub2sfiRqv'
initiator_address = '013803e566cdc065c415b14a1f082f240e8cc81a6f13fd01ef59e94620601a5a2f26e83b806091'
initiator_amount = 0.01234
participant_amount = 0.5
testnet = True

# initiator = j.tools.atomicswap.get_btc_initiator('localhost:2200', initiator_amount,
#                                                 participant_address, testnet)
# participant = j.tools.atomicswap.get_tft_participant('localhost:2222', participant_amount,
#                                                 initiator_address, testnet)

# import IPython
# IPython.embed()


# import pdb; pdb.set_trace()
btc_prefab = j.tools.prefab.getFromSSH('localhost', port=2200)
tft_prefab = j.tools.prefab.getFromSSH('localhost', port=2222)
j.tools.atomicswap.execute(initiator_prefab=btc_prefab, initiator_address=initiator_address,
                          initiator_amount='{}BTC'.format(initiator_amount),
                          participant_prefab=tft_prefab,
                          participant_address=participant_address,
                          participant_amount='{}TFT'.format(participant_amount),
                          testnet=testnet)


# initiate_cmd = 'btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 --force-yes initiate {} 0.01234'.format(participant_address)
#
# rc, out, err = btc_prefab.core.run(initiate_cmd)
#
# out= """Secret:      d65fa37cf91c74a917d3bbde2a031ccbd11538babc3057cd4bc2f9b0809e90ef\nSecret hash: 0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e\n\nContract fee: 0.00000166 BTC (0.00000672 BTC/kB)\nRefund fee:   0.00000297 BTC (0.00001021 BTC/kB)\n\nContract (2MvpTsm9wXHNYWaQCGs9jHoaYJ42cieRjfd):\n6382012088a8200900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e8876a9145d4e3d61ad2fa7888473e99007280b3161e7fdf2670494d7335bb17576a9147c6076e1594229d2e3267a2b67102045397a232c6888ac\n\nContract transaction (7daaac73d7ed508f6fae3fe03d397a0fdc423b84dd19127c9882dc9e8b084a2d):\n02000000000101da2ad7719034ff29c595997ba5cbf1b26d9037e5bc81b0b0f4f8b7a43e679b5a0000000017160014547e2929999a8ae11963ad285e07fd8789d0145afeffffff02fb4a64030000000017a914fcc15ebf5dce3f55e7eb11b69e65a95d263a55ac8750d412000000000017a9142731b263e593f1d8c1c00d0287169460b1643d7a870247304402202c69331697c856f43d8ccfdf90ae5dc5b083384028a1feb8d6558aa9ebf2471702201b398d68d36f5199ded51cd1849927567913e507a74e345bb2d9f6031d86cca50121022aae89285d0f5996f1fe7dd004e21883d40a2ad6dba7b94bba0ea219fd9595a300000000\n\nRefund transaction (a36e15da8d7aa3d304db61c5df72b581a83686b71d4000c4e532fe723ab7161a):\n02000000012d4a088b9edc82987c1219dd843b42dc0f7a393de03fae6f8f50edd773acaa7d01000000ce473044022050b40d28c276f11064920482d40381ab6dfaabfb78332a64df7a11dd916192c7022077696247c61c6c949196b1a24cc5be6a3ee351b1bdd0cfd5dc65d5d244021c970121021d97c38fe6e28d76eb0eb4e57f7859a38f51eb4e3d976355c103a2dd3ba2632a004c616382012088a8200900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e8876a9145d4e3d61ad2fa7888473e99007280b3161e7fdf2670494d7335bb17576a9147c6076e1594229d2e3267a2b67102045397a232c6888ac000000000127d31200000000001976a9147777c50fbe87c187f9e73155815209fc47d5633388ac94d7335b\n\nPublished contract transaction (7daaac73d7ed508f6fae3fe03d397a0fdc423b84dd19127c9882dc9e8b084a2d)"""
#
# # {'secret': 'd65fa37cf91c74a917d3bbde2a031ccbd11538babc3057cd4bc2f9b0809e90ef',
# #  'secret_hash': '0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e',
# #  'contract_addr': '2MvpTsm9wXHNYWaQCGs9jHoaYJ42cieRjfd',
# #  'contract': '6382012088a8200900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e8876a9145d4e3d61ad2fa7888473e99007280b3161e7fdf2670494d7335bb17576a9147c6076e1594229d2e3267a2b67102045397a232c6888ac',
# #  'contract_txn_addr': '7daaac73d7ed508f6fae3fe03d397a0fdc423b84dd19127c9882dc9e8b084a2d',
# #  'contract_txn': '02000000000101da2ad7719034ff29c595997ba5cbf1b26d9037e5bc81b0b0f4f8b7a43e679b5a0000000017160014547e2929999a8ae11963ad285e07fd8789d0145afeffffff02fb4a64030000000017a914fcc15ebf5dce3f55e7eb11b69e65a95d263a55ac8750d412000000000017a9142731b263e593f1d8c1c00d0287169460b1643d7a870247304402202c69331697c856f43d8ccfdf90ae5dc5b083384028a1feb8d6558aa9ebf2471702201b398d68d36f5199ded51cd1849927567913e507a74e345bb2d9f6031d86cca50121022aae89285d0f5996f1fe7dd004e21883d40a2ad6dba7b94bba0ea219fd9595a300000000',
# #  'refund_txn_addr': 'a36e15da8d7aa3d304db61c5df72b581a83686b71d4000c4e532fe723ab7161a',
# #  'refund_txn': '02000000012d4a088b9edc82987c1219dd843b42dc0f7a393de03fae6f8f50edd773acaa7d01000000ce473044022050b40d28c276f11064920482d40381ab6dfaabfb78332a64df7a11dd916192c7022077696247c61c6c949196b1a24cc5be6a3ee351b1bdd0cfd5dc65d5d244021c970121021d97c38fe6e28d76eb0eb4e57f7859a38f51eb4e3d976355c103a2dd3ba2632a004c616382012088a8200900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e8876a9145d4e3d61ad2fa7888473e99007280b3161e7fdf2670494d7335bb17576a9147c6076e1594229d2e3267a2b67102045397a232c6888ac000000000127d31200000000001976a9147777c50fbe87c187f9e73155815209fc47d5633388ac94d7335b',
# #  'published_contract_txn_address': '7daaac73d7ed508f6fae3fe03d397a0fdc423b84dd19127c9882dc9e8b084a2d'}
# #
# contract = '6382012088a8200900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e8876a9145d4e3d61ad2fa7888473e99007280b3161e7fdf2670494d7335bb17576a9147c6076e1594229d2e3267a2b67102045397a232c6888ac'
# contract_txn = '02000000000101da2ad7719034ff29c595997ba5cbf1b26d9037e5bc81b0b0f4f8b7a43e679b5a0000000017160014547e2929999a8ae11963ad285e07fd8789d0145afeffffff02fb4a64030000000017a914fcc15ebf5dce3f55e7eb11b69e65a95d263a55ac8750d412000000000017a9142731b263e593f1d8c1c00d0287169460b1643d7a870247304402202c69331697c856f43d8ccfdf90ae5dc5b083384028a1feb8d6558aa9ebf2471702201b398d68d36f5199ded51cd1849927567913e507a74e345bb2d9f6031d86cca50121022aae89285d0f5996f1fe7dd004e21883d40a2ad6dba7b94bba0ea219fd9595a300000000'
# audit_cmd = 'btcatomicswap --testnet -s localhost:8332 auditcontract {} {}'.format(contract, contract_txn)
#
# rc, out, err = tft_prefab.core.run(audit_cmd)
#
# out = """Contract address:        2MvpTsm9wXHNYWaQCGs9jHoaYJ42cieRjfd\nContract value:          0.01234 BTC\nRecipient address:       mp2Js67GxeneGYzPeh9zZqYdikr4kFphCq\nAuthor's refund address: mrrbeJYhWD3hrAwa1ikLogwySrCs8Cc2fc\n\nSecret hash: 0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e\n\nLocktime: 2018-06-27 18:29:40 +0000 UTC\nLocktime reached in 47h33m57s"""
#
# secret_hash = '0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e'
#
# participate_cmd = "tfchainc atomicswap -y --encoding json participate {} .5 {}".format(initiator_address, secret_hash)
# rc, out, err = tft_prefab.core.run(participate_cmd)
# out = """{"coins":"500000000","contract":{"sender":"012ffd03d1b4d39ba9df8294bb5135a0a69768494a54e4df0c0eb817309b6a7fba795e4ac1f4ff","receiver":"0108031a2111cec5427954fae23fdd6a0cc21d9ab91cf0e878af9d2bb0081e9c1246da7c1e2346","hashedsecret":"0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e","timelock":1530126270},"contractid":"02806e2cfa3aa87e2ea41d4c1f1bf8bf2b73d167eb3df610b7b364633426b8215e607e40db08b1","outputid":"e27bfac78c16e7690b5cb477f1602e0f6b074522d198d4733dd03d148cac4024","transactionid":"09bb77d6555488103f59709d27f0679fcf4d86dfa3ae77dbb06d976aeccc947e"}"""
#
# output_id = 'e27bfac78c16e7690b5cb477f1602e0f6b074522d198d4733dd03d148cac4024'
# recipient_addr = '0108031a2111cec5427954fae23fdd6a0cc21d9ab91cf0e878af9d2bb0081e9c1246da7c1e2346'
# refund_addr = '012ffd03d1b4d39ba9df8294bb5135a0a69768494a54e4df0c0eb817309b6a7fba795e4ac1f4ff'
# timelock = 1530126270
# secret_hash = '0900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e'
# amount = .5
#
# audit_cmd = 'tfchainc atomicswap -y --encoding json auditcontract {} --receiver {} --secrethash {} --amount {}'.format(output_id, recipient_addr, secret_hash, amount)
#
# rc, out, err = btc_prefab.core.run(audit_cmd)
#
# secret = 'd65fa37cf91c74a917d3bbde2a031ccbd11538babc3057cd4bc2f9b0809e90ef'
# redeem_cmd = 'tfchainc atomicswap redeem {} {} -y --encoding json '.format(output_id, secret)
# rc, out, err = btc_prefab.core.run(redeem_cmd)
#
# rpcuser, rpcpass, addr = 'user', 'pass', 'localhost:8332'
# reverse_redeem_cmd = 'btcatomicswap --testnet -s {} --rpcuser={} --rpcpass={} --force-yes redeem {} {} {}'.format(addr,
#                                                                                      rpcuser , rpcpass, contract, contract_txn, secret)
#
# _, out, _, tft_prefab.core.run(reverse_redeem_cmd)
# # In [97]: out
# # Out[97]: 'Redeem fee: 0.0000033 BTC (0.00001015 BTC/kB)\n\nRedeem transaction (f202c74569424241c9f75f432af838a297399e139a2928c396d5ad0606212057):\n02000000012d4a088b9edc82987c1219dd843b42dc0f7a393de03fae6f8f50edd773acaa7d01000000f048304502210082ede14fc6661fbbf58f084314403e4adbebb3a986afbe7379db909d80017d8902202f25c29ef0e868ac16847c413d2ac7f6aa1fa04e5f791ca511dd61d71772f04b0121020b7b2ce577f86d831da8952c314442fb57c160db825d454f64993930874f093a20d65fa37cf91c74a917d3bbde2a031ccbd11538babc3057cd4bc2f9b0809e90ef514c616382012088a8200900e02c2b413ad422c107862b670c7980fa24956e60699436f652ff56d98d4e8876a9145d4e3d61ad2fa7888473e99007280b3161e7fdf2670494d7335bb17576a9147c6076e1594229d2e3267a2b67102045397a232c6888acffffffff0106d31200000000001976a914e30807b95a6d53eadca9043ede8bcc29b4cbf8d888ac94d7335b\n\nPublished redeem transaction (f202c74569424241c9f75f432af838a297399e139a2928c396d5ad0606212057)'
