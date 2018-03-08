"""
Test module for RivineWallet js9 client
"""


from mnemonic import Mnemonic
from JumpScale9Lib.clients.rivine.RivineWallet import RivineWallet

# create a random seed
m = Mnemonic('english')
seed = m.generate()

# use specific seed
seed = 'festival mobile negative nest valid cheese pulp alpha relax language friend vast'

expected_unlockhashes = [
    '2d85a10ad31f2d505768be5efb417de565a53364d7f0c69a888ca764f4bdbcbb',
    '59e5933416affb97748d5e94fa64f97305075c4ebf971c09a64977839b7087b3',
    '65e5838cfee444cbf98661e2648918ad7b0d622e9b600f1b8271161874cd1d6c',
    '7c75ddbfe744022c2b9be8f38b7049e4878b3e5030910447b0083af2ac5e20db',
    'bc961fa13fd17ea13268d24bf502506325729c07da867d8dc64363a2af9955f6'
]

# create a wallet based on the generated Seed
rivine_wallet = RivineWallet(seed=seed, bc_network='http://185.69.166.13:2015', nr_keys_per_seed=5)
actual_unlockhashes = [key for key in rivine_wallet.keys.keys()] 

assert set(expected_unlockhashes) ==  set(actual_unlockhashes), "Unlockhashes do not match" 

assert type(rivine_wallet.get_current_chain_height()) == int

expected_address_info = {'hashtype': 'blockid', 'block': {'minerpayoutids': ['c9b61e659934fe073e25d54c408413f4c851a0c41e933dda6d852a0fdc53ef47'], 'transactions': [{'id': '21a5a2eab1b5140024fa20b4641451701a5a9f8c88fcbc30d14f699e020d2c9e', 'height': 1487, 'parent': 'c978699d38b941b9fe43661ec95e08bbf04accac3557c055ea8940fa53232ed8', 'rawtransaction': {'coininputs': None, 'coinoutputs': None, 'blockstakeinputs': [{'parentid': 'a9a48e5b62176d5b1992550b0b02be800b8295a1f242b64e0784a9868a5e0ba5', 'unlockconditions': {'timelock': 0, 'publickeys': [{'algorithm': 'ed25519', 'key': 'JqnLW7M2JNg75utM8MmIMQhO98PQ5ankwggTSVqjDxc='}], 'signaturesrequired': 1}}], 'blockstakeoutputs': [{'value': '333334', 'unlockhash': '3e4ffa39393480812eb23fd0be49921efa035c19ffe37088a11af1bb01ac613960f7275a8cd1'}], 'minerfees': None, 'arbitrarydata': None, 'transactionsignatures': [{'parentid': 'a9a48e5b62176d5b1992550b0b02be800b8295a1f242b64e0784a9868a5e0ba5', 'publickeyindex': 0, 'timelock': 0, 'coveredfields': {'wholetransaction': True, 'coininputs': None, 'coinoutputs': None, 'blockstakeinputs': None, 'blockstakeoutputs': None, 'minerfees': None, 'arbitrarydata': None, 'transactionsignatures': None}, 'signature': '+RlleX99Mun4Pq9ghKp5lE2X8U+yzO6IlYIONGVcRD0Ua5Uy7n1EOLRjrPBZlSrimigs5bG3QS2PBiVSfrkeBg=='}]}, 'coininputoutputs': None, 'coinoutputids': None, 'blockstakeinputoutputs': [{'value': '333334', 'unlockhash': '3e4ffa39393480812eb23fd0be49921efa035c19ffe37088a11af1bb01ac613960f7275a8cd1'}], 'blockstakeoutputids': ['b678fa9db634cc46b508a2cf4127bad67b109b2e0f38072ac82a7389e9430886']}], 'rawblock': {'parentid': 'e8e82e49e016e47a5ec1acd217f76d767dc69a91e9c43fdc26f230517945d440', 'timestamp': 1520436758, 'pobsindexes': {'BlockHeight': 1486, 'TransactionIndex': 0, 'OutputIndex': 0}, 'minerpayouts': [{'value': '10000000000000000000000000', 'unlockhash': '3e4ffa39393480812eb23fd0be49921efa035c19ffe37088a11af1bb01ac613960f7275a8cd1'}], 'transactions': [{'coininputs': None, 'coinoutputs': None, 'blockstakeinputs': [{'parentid': 'a9a48e5b62176d5b1992550b0b02be800b8295a1f242b64e0784a9868a5e0ba5', 'unlockconditions': {'timelock': 0, 'publickeys': [{'algorithm': 'ed25519', 'key': 'JqnLW7M2JNg75utM8MmIMQhO98PQ5ankwggTSVqjDxc='}], 'signaturesrequired': 1}}], 'blockstakeoutputs': [{'value': '333334', 'unlockhash': '3e4ffa39393480812eb23fd0be49921efa035c19ffe37088a11af1bb01ac613960f7275a8cd1'}], 'minerfees': None, 'arbitrarydata': None, 'transactionsignatures': [{'parentid': 'a9a48e5b62176d5b1992550b0b02be800b8295a1f242b64e0784a9868a5e0ba5', 'publickeyindex': 0, 'timelock': 0, 'coveredfields': {'wholetransaction': True, 'coininputs': None, 'coinoutputs': None, 'blockstakeinputs': None, 'blockstakeoutputs': None, 'minerfees': None, 'arbitrarydata': None, 'transactionsignatures': None}, 'signature': '+RlleX99Mun4Pq9ghKp5lE2X8U+yzO6IlYIONGVcRD0Ua5Uy7n1EOLRjrPBZlSrimigs5bG3QS2PBiVSfrkeBg=='}]}]}, 'blockid': 'c978699d38b941b9fe43661ec95e08bbf04accac3557c055ea8940fa53232ed8', 'difficulty': '124133008', 'estimatedactivebs': '858784', 'height': 1487, 'maturitytimestamp': 1520416867, 'target': [0, 0, 0, 34, 153, 135, 58, 94, 203, 128, 205, 131, 100, 16, 29, 188, 101, 79, 63, 58, 188, 78, 158, 187, 180, 59, 105, 210, 139, 212, 214, 141], 'totalcoins': '0', 'minerpayoutcount': 1487, 'transactioncount': 1504, 'coininputcount': 27, 'coinoutputcount': 37, 'blockstakeinputcount': 1487, 'blockstakeoutputcount': 1490, 'minerfeecount': 18, 'arbitrarydatacount': 0, 'transactionsignaturecount': 1514}, 'blocks': None, 'transaction': {'id': '0000000000000000000000000000000000000000000000000000000000000000', 'height': 0, 'parent': '0000000000000000000000000000000000000000000000000000000000000000', 'rawtransaction': {'coininputs': None, 'coinoutputs': None, 'blockstakeinputs': None, 'blockstakeoutputs': None, 'minerfees': None, 'arbitrarydata': None, 'transactionsignatures': None}, 'coininputoutputs': None, 'coinoutputids': None, 'blockstakeinputoutputs': None, 'blockstakeoutputids': None}, 'transactions': None}
assert rivine_wallet.check_address(address='c978699d38b941b9fe43661ec95e08bbf04accac3557c055ea8940fa53232ed8') == expected_address_info, "Expected address info is not the same as check_address found"



