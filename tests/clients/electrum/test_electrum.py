"""
Test script to test different commands of electrum wallet
"""

import os
from js9 import j

BASE_VAR_DIR = '/opt/var/data/'
RPC_USER = 'user'
RPC_PASS = 'pass'
RPC_PORT = 7777
RPC_HOST = 'localhost'

# you can generate a seed using
# from electrum.mnemonic import Mnemonic
# Mnemonic('n').make_seed(num_bits=256)
SEED = 'net shield travel gather west quote afraid salad spawn casino smile smoke boil flower rescue image antenna soda silent bounce husband tail square phrase'


def _create_electrum_dir():
    """
    Creates a directory that should be used as a the home directory of electrum
    """
    root_dir = os.path.join(BASE_VAR_DIR, 'electrum')
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    else:
        print('Electrum root dir {} exists'.format(root_dir))
    return root_dir



def _start_daemon_and_get_client(wallet_name):
    """
    Starts a daemon and create a client
    """
    electrum_dir = _create_electrum_dir()
    # check if running already
    process_name = j.sal.process.getProcessByPort(RPC_PORT)
    if process_name and 'electrum' in process_name:
        print("Electrum daemon is already running")
    elif process_name:
        raise RuntimeError("Port {} already in use by process {}".format(RPC_PORT, process_name))
    # not running
    if not process_name:
        base_cmd = 'electrum --testnet -D {}'.format(electrum_dir)
        cmds = [
                '{} setconfig rpcuser {}'.format(base_cmd, RPC_USER),
                '{} setconfig rpcpassword {}'.format(base_cmd, RPC_PASS),
                '{} setconfig rpcport {}'.format(base_cmd, RPC_PORT),
                '{} setconfig rpchost {}'.format(base_cmd, RPC_HOST),
                '{} daemon 1>/dev/null 2>&1 &'.format(base_cmd),
                ]
        prefab = j.tools.prefab.local
        for cmd in cmds:
            prefab.core.run(cmd)

    client_data = {
        'server': "{}:{}:s".format(RPC_HOST, RPC_PORT),
        'rpc_user': RPC_USER,
        'rpc_pass_': RPC_PASS,
        'seed_': SEED,
        'password_': "pass",
        "passphrase_": "",
        "electrum_path": electrum_dir,
        "testnet": 1
    }

    electrum_cl = j.clients.electrum.get(instance=wallet_name,
                                                    data=client_data)
    electrum_cl.config.save()
    return electrum_cl


if __name__ == '__main__':
    electrum_cl = _start_daemon_and_get_client(wallet_name='mytestwallet')
    import IPython
    IPython.embed()
