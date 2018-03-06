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



