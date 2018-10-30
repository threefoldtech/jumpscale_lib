#python script for 0-core testcases
import os
from argparse import ArgumentParser
from subprocess import Popen, PIPE
import random
import uuid
import time
import shlex
from jumpscale import j
from termcolor import colored
from multiprocessing import Process, Manager

SETUP_ENV_SCRIPT= "tests/integration_tests/travis/setup_env.sh"
SETUP_ENV_SCRIPT_NAME = "setup_env.sh"
manage = Manager()
JS_RESULTS_que = manage.Queue()   

class Utils(object):
    def __init__(self, options):
        self.options = options

    def run_cmd(self, cmd, timeout=20):
        now = time.time()
        while time.time() < now + timeout:
            sub = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
            out, err = sub.communicate()
            if sub.returncode == 0:
                return out.decode('utf-8')
            elif any(x in err.decode('utf-8') for x in ['Connection refused', 'No route to host']):
                time.sleep(1)
                continue
            else:
                break
        raise RuntimeError("Failed to execute command.\n\ncommand:\n{}\n\n{}".format(cmd, err.decode('utf-8')))

    def stream_run_cmd(self, cmd):
        sub = Popen(shlex.split(cmd), stdout=PIPE)
        while True:
            out = sub.stdout.readline()
            if out == b'' and sub.poll() is not None:
                break
            if out:
                print(out.strip())
        rc = sub.poll()
        return rc

    def send_script_to_remote_machine(self, script, ip, port):
        templ = 'scp -o StrictHostKeyChecking=no -r -o UserKnownHostsFile=/dev/null -P {} {} root@{}:'
        cmd = templ.format(port, script, ip)
        self.run_cmd(cmd)

    def run_cmd_on_remote_machine(self, cmd, ip, port):
        templ = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p {} root@{} {}'
        cmd = templ.format(port, ip, cmd)
        return self.stream_run_cmd(cmd)

    def run_cmd_on_remote_machine_without_stream(self, cmd, ip, port):
        templ = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p {} root@{} {}'
        cmd = templ.format(port, ip, cmd)
        return self.run_cmd(cmd)


    def create_disk(self, zos_client):
        zdb_name = str(uuid.uuid4())[0:8]
        zdb = zos_client.primitives.create_zerodb(name=zdb_name, path='/mnt/zdbs/sda',
                                                  mode='user', sync=False, admin='mypassword')
        zdb.namespaces.add(name='mynamespace', size=50, password='namespacepassword', public=True)
        zdb.deploy()
        disk = zos_client.primitives.create_disk('mydisk', zdb, size=50)
        disk.deploy()
        return disk

    def random_mac(self):
        return "52:54:00:%02x:%02x:%02x" % (random.randint(0, 255),
                                            random.randint(0, 255),
                                            random.randint(0, 255))

    def get_farm_available_node_to_execute_testcases(self):
        capacity = j.clients.threefold_directory.get(interactive=False)
        resp = capacity.api.ListCapacity(query_params={'farmer': 'tlre'})[1]
        nodes = resp.json() #nodes
        return random.choice(nodes)

    def random_string(self, size=10):
        return str(uuid.uuid4()).replace('-', '')[:size]     

    def create_ubuntu_vm(self, zos_client, ubuntu_port):
        print('* Creating ubuntu vm to fire the testsuite from')
        keypath = '/root/.ssh/id_rsa.pub'
        if not os.path.isfile(keypath):
            os.system("echo  | ssh-keygen -P ''")
        with open(keypath, "r") as key:
            pub_key = key.read()
        pub_key.replace('\n', '')
        vm_ubuntu_name = "ubuntu{}".format(self.random_string())
        vm_ubuntu = zos_client.primitives.create_virtual_machine(name=vm_ubuntu_name, type_='ubuntu:lts')
        vm_ubuntu.nics.add(name='default_nic', type_='default')
        vm_ubuntu.configs.add('sshkey', '/root/.ssh/authorized_keys', pub_key)
        vm_ubuntu.ports.add('ssh_port', ubuntu_port, 22)
        vm_ubuntu.vcpus = 4
        vm_ubuntu.memory = 8192
        vm_ubuntu.deploy()
        return vm_ubuntu

def main(options):
    utils = Utils(options)
    zos_client = j.clients.zos.get('zos-kds-farm', data={'host': '{}'.format(options.zos_ip)})

    # Setup the env to run testcases on it 
    ubuntu_port = int(options.ubuntu_port)
    JS_FLAG = options.js_flag
    if JS_FLAG == "True":
        vm = utils.create_ubuntu_vm(zos_client, ubuntu_port)
    # Send the script to setup the envirnment and run testcases 
    utils.send_script_to_remote_machine(SETUP_ENV_SCRIPT, options.zos_ip, ubuntu_port)
    # get available node to run testcaases against it 
    print('* get available node to run test cases on it ')
    zos_available_node = utils.get_farm_available_node_to_execute_testcases()
    node_ip = zos_available_node["robot_address"][7:-5] 
    print('* The available node ip {} '.format(node_ip))
    
    # Access the ubuntu vm and install requirements  
    cmd = 'bash {script} {branch} {nodeip} {zt_token}'.format(script=SETUP_ENV_SCRIPT_NAME, branch="sal_testcases", nodeip=node_ip, zt_token=options.zt_token)
    utils.run_cmd_on_remote_machine(cmd, options.zos_ip, ubuntu_port)

        
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-z", "--zos_ip", type=str, dest="zos_ip", required=True,
                        help="IP of the zeroos machine that will be used")
    parser.add_argument("-b", "--branch", type=str, dest="branch", required=True,
                        help="0-core branch that the tests will run from")
    parser.add_argument("-jp", "--ubuntu_port", type=str, dest="ubuntu_port", required=False,
                        help="if you have jumpscale machine on the node provide its port" )
    parser.add_argument("-jf", "--js_flag", type=str, dest="js_flag", required=False,
                        help="flag if you have jumpscale machine" )
    parser.add_argument("-t", "--zt_token", type=str, dest="zt_token", default='sgtQtwEMbRcDgKgtHEMzYfd2T7dxtbed', required=True,
                        help="zerotier token that will be used for the core0 tests")
    options = parser.parse_args()
    main(options)

