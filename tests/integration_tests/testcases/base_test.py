from testconfig import config
from termcolor import colored
import unittest
from jumpscale import j
import uuid, time, os
import subprocess
from framework.utils import Utils
from framework.base.vms import VM
from framework.base.gw import GW
from framework.base.zdb import ZDB
import random

BASEFLIST = 'https://hub.grid.tf/tf-bootable/{}.flist'
ZEROOSFLIST = 'https://hub.grid.tf/tf-bootable/zero-os-bootable.flist'
NODE_CLIENT = str(uuid.uuid4()).replace('-', '')[:10]
ZT_CLIENT_INSTANCE = str(uuid.uuid4()).replace('-', '')[:10]


class BaseTest(Utils):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        self = cls()
        cls.node_sal = j.clients.zos.get(NODE_CLIENT, data={'host': config['main']['nodeip']})
        cls.node_info = self.get_zos_info()
        cls.vm_flist = "https://hub.grid.tf/tf-bootable/ubuntu:16.04.flist"
        cls.vm = VM
        cls.gw = GW
        cls.zdb = ZDB
        cls.ssh_key = self.load_ssh_key()
        cls.zt_token = config['main']['zt_token']
        cls.zt_network_name = self.random_string()
        cls.zt_client = j.clients.zerotier.get(instance=ZT_CLIENT_INSTANCE, data={'token_': cls.zt_token})
        cls.zt_network = cls.zt_client.network_create(public=False, name=self.zt_network_name, auto_assign=True, subnet='10.147.19.0/24')
        cls.host_ip = self.host_join_zt()

    @classmethod
    def tearDownClass(cls):
        self = cls()
        self.host_leave_zt()

    def setUp(self):
        super(BaseTest, self).setUp()

    def tearDown(self):
        pass

    def host_leave_zt(self, zt_network=None):

        zt_network = zt_network or self.zt_network
        j.tools.prefab.local.network.zerotier.network_leave(zt_network.id)
        
    def random_string(self, size=10):
        return str(uuid.uuid4()).replace('-', '')[:size]        

    def set_vm_default_values(self, os_type, os_version=None):

        vm_parms = {'flist':"",
                    'cpu': random.randint(1, self.node_info['core']),
                    'memory': 1024, #random.randint(1, self.node_info['memory']) * 1024,
                    'name': self.random_string(),
                    'nics': [],
                    'configs': [{'path': '/root/.ssh/authorized_keys',
                                 'content': self.ssh_key,
                                 'name': 'sshkey'}],
                    'ports': [],
                    'mounts':[],
                    'disks':[],
                    'tags':[]
                    }
        if os_type == 'zero-os':
            version = os_version or 'master'
            vm_parms['ipxeurl'] = 'https://bootstrap.grid.tf/ipxe/{}/0/development'.format(version)
            vm_parms['flist'] = ZEROOSFLIST

        elif os_type == 'ubuntu':
            version = os_version or 'lts'
            flistname = '{}:{}'.format(os_type, version)
            vm_parms['flist'] = BASEFLIST.format(flistname)

        return vm_parms

    def add_zerotier_network_to_vm(self, vm, network=None, name=None):
        network = network or self.zt_network
        vm.nics.add_zerotier(network=network, name=name)

    def update_default_data(self, old_data, new_data):
        for key in new_data:
            old_data[key] = new_data[key]
        return old_data

    def get_machine_zerotier_ip(self, ztIdentity, timeout=None, zt_client=None, zt_network=None):
        ztAddress = ztIdentity.split(':')[0]
        zt_client = zt_client or self.zt_client
        zt_network = zt_network or self.zt_network
        for _ in range(300):
            try:
                member = zt_network.member_get(address=ztAddress)
                member.timeout = None
                member_ip = member.get_private_ip(timeout)
                return member_ip
            except (RuntimeError, ValueError) as e:
                print(colored('Failed to retreive zt ip: %s', str(e), 'red'))
                time.sleep(1)

    def get_zos_info(self):
        info = self.node_sal.capacity.total_report()
        node_info = {'ssd': int(info.SRU), 'hdd': int(info.HRU), 'core': info.CRU,
                     'memory': int(info.MRU)}
        return node_info

    def load_ssh_key(self):
        if os.path.exists('/tmp/id_rsa.pub'):
            with open('/tmp/id_rsa.pub', 'r') as file:
                ssh = file.readline().replace('\n', '')
        else:              
            print(colored('[+] Generate sshkey.', 'white'))
            cmd = 'ssh-keygen -t rsa -f /tmp/id_rsa -q -P ""; eval `ssh-agent -s`; ssh-add  /tmp/id_rsa'
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ssh = self.load_ssh_key()
        return ssh


    def execute_command(self, ip, cmd):
        target = """ssh -o "StrictHostKeyChecking no" root@%s '%s'""" % (ip, cmd)
        ssh = subprocess.Popen(target, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        error = ssh.stderr.readlines()
        return result, error

    def host_join_zt(self, zt_network=None):
        zt_network = zt_network or self.zt_network
        j.tools.prefab.local.network.zerotier.network_join(network_id=zt_network.id)
        zt_machine_addr = j.tools.prefab.local.network.zerotier.get_zerotier_machine_address()
        time.sleep(30)
        for _ in range(20):
            try:
                host_member = zt_network.member_get(address=zt_machine_addr)
                break
            except:
                time.sleep(30)
        else:
            host_member = zt_network.member_get(address=zt_machine_addr)
        host_member.authorize()
        time.sleep(30)
        host_ip = host_member.private_ip
        return host_ip 

    def ssh_vm_execute_command(self, vm_ip, cmd):
        for _ in range(10):            
            result, error = self.execute_command(ip=vm_ip, cmd=cmd)
            if error:
                print(colored(' [-] Execute command error : {}'.format(error), 'red'))
                time.sleep(30)
            else:
                print(colored(' [+] Execute command passed.', 'green'))
                return result
        else:
            raise RuntimeError(colored(' [-] {}'.format(error), 'red'))

    def set_gw_default_values(self, status="halted", name=None):
        gw_parms = {
                    'name': name or self.random_string(),
                    'status': status,
                    'hostname': self.random_string(),
                    'networks': [],
                    'portforwards': [],
                    'httpproxies': [],
                    'domain': 'domain',
                    'certificates': [],
                    'routes': [],
                    'ztIdentity': '',
                    }

        return gw_parms

    def get_gw_network(self, gw, name):
        networks = gw.networks.list()
        network = [network for network in networks if network.name == name ]
        return network

