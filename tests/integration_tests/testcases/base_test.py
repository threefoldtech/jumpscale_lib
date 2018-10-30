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
        cls.node_info, cls.disks_info = self.get_zos_info()
        cls.disks_mount_paths = self.zdb_mounts()
        cls.vm_flist = "https://hub.grid.tf/tf-bootable/ubuntu:16.04.flist"
        cls.vm = VM
        cls.gw = GW
        cls.zdb = ZDB
        cls.ssh_key = self.load_ssh_key()
        cls.zt_token = config['main']['zt_token']
        cls.node_ip = config['main']['nodeip']
        cls.zt_network_name = self.random_string()
        cls.zt_client = j.clients.zerotier.get(instance=ZT_CLIENT_INSTANCE, data={'token_': cls.zt_token})
        cls.zt_network = cls.zt_client.network_create(public=False, name=self.zt_network_name, auto_assign=True, subnet='10.147.17.0/24')
        cls.host_ip = self.host_join_zt()
        cls.vms = []
        cls.zdbs = []


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
                    'memory':  random.randint(1, 3) * 1024,
                    'cpu':  random.randint(1, len(self.node_sal.client.info.cpu())),
                    'name': self.random_string(),
                    'nics': [],
                    'configs': [{'path': '/root/.ssh/authorized_keys',
                                 'content': self.ssh_key,
                                 'name': 'sshkey'}],
                    'ports': [],
                    'mounts':[],
                    'kernelArgs':[],
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

    def update_default_data(self, old_data, new_data):
        for key in new_data:
            old_data[key] = new_data[key]
        return old_data

    def get_zerotier_ip(self, ztIdentity, timeout=None, zt_client=None, zt_network=None):
        ztAddress = ztIdentity.split(':')[0]
        zt_client = zt_client or self.zt_client
        zt_network = zt_network or self.zt_network
        for _ in range(30):
            try:
                member = zt_network.member_get(address=ztAddress)
                member.timeout = None
                member_ip = member.get_private_ip(timeout)
                return member_ip
            except (RuntimeError, ValueError) as e:
                time.sleep(10)
        else:
            raise RuntimeError("Failed to retreive zt ip: Cannot get private ip address for zerotier member")

    def get_zos_info(self):
        info = self.node_sal.capacity.total_report()
        node_info = {'ssd': int(info.SRU), 'hdd': int(info.HRU), 'core': int(info.CRU),
                     'memory': int(info.MRU)}
        disks_info = {'ssd': int(info.SRU), 'hdd': int(info.HRU)}
        return node_info, disks_info

    def load_ssh_key(self):

        home_user = os.path.expanduser('~')
        if os.path.exists('{}/.ssh/id_rsa.pub'.format(home_user)):
            with open('{}/.ssh/id_rsa.pub'.format(home_user), 'r') as file:
                ssh = file.readline().replace('\n', '')
        else:              
            cmd = 'ssh-keygen -t rsa -N "" -f {}/.ssh/id_rsa -q -P ""; ssh-add {}/.ssh/id_rsa'.format(home_user, home_user)
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ssh = self.load_ssh_key()
        return ssh

    def execute_command(self, cmd, ip='', port=22):
        target = "ssh -o 'StrictHostKeyChecking no' -p {} root@{} '{}'".format(port, ip, cmd)
        response = subprocess.run(target, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # "response" has stderr, stdout and returncode(should be 0 in successful case)
        return response

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

    def zos_node_join_zt(self, network_id):
        self.node_sal.client.zerotier.join(network_id)
        ztIdentity = self.node_sal.client.zerotier.info()['publicIdentity']
        node_ip = self.get_machine_zerotier_ip(ztIdentity)
        return node_ip
        
    def ssh_vm_execute_command(self, vm_ip, cmd, port=22):
        for _ in range(10):            
            resposne = self.execute_command(ip=vm_ip, cmd=cmd, port=port)
            if resposne.returncode:
                time.sleep(25)
            else:
                return resposne.stdout.strip()
        else:
            raise RuntimeError(colored(' [-] {}'.format(resposne.stderr.strip()), 'red'))

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

    def check_vnc_connection(self, vnc_ip_port):
        vnc = 'vncdotool -s {} type {} key enter'.format(vnc_ip_port, repr('ls'))
        response = subprocess.run(vnc, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response

    def get_gateway_container(self,gw_name):
        containers = self.node_sal.client.container.list()
        gw_container = [ container for _ ,container in containers.items() if container['container']['arguments']['hostname'] == gw_name][0]
        return gw_container

    def zdb_mounts(self):
        disk_mount=[]
        self.node_sal.zerodbs.prepare()
        storage_pools = self.node_sal.storagepools.list()
        for sp in storage_pools:
            if sp.name == 'zos-cache':
                continue
            try:
                file_system = sp.get('zdb')
            except Exception:
                continue
            disk_name = sp.device[len('/dev/'):-1]
            zdb_mount = file_system.path
            disk_mount.append({'disk': disk_name, 'mountpoint': zdb_mount})
        return disk_mount

    def get_disk_mount_path(self, disk_type):
        disk_RO = '0' if disk_type == "ssd" else '1'
        for disk in self.disks_mount_paths:
            self.disk_name = disk['disk']
            disk_info = self.node_sal.client.disk.getinfo(self.disk_name)
            if disk_info['ro'] == disk_RO:
                disk_path = disk['mountpoint']
                return disk_path

    def get_disks_type(self):
        disks = self.node_sal.client.disk.list()
        disks_type = {'ssd': 0, 'hdd': 0}
        for disk in disks:
            if int(disk["ro"])==0:
                disks_type["ssd"]+=1
            else:
                disks_type["hdd"]+=1
        return disks_type

    def select_disk_type(self):
        disks_info = self.get_disks_type()
        if disks_info['hdd'] > disks_info['ssd']:
            disk_type = 'hdd'
        else:
            disk_type = 'ssd'
            
        return disk_type

    def get_disk_size(self):
        size_bytes = self.node_sal.client.disk.getinfo(self.disk_name)['size']
        size_gb = size_bytes / 1024**3
        return size_gb

    def set_vdisk_default_data(self, name=None):
        disk_params = {
                        'name': name or self.random_string(),
                        'mountPoint': "",
                        'filesystem': "",
                        'mode': 'user',
                        'public': False,
                        'label': '',
                      }
        disk_type = self.select_disk_type()
        disk_size = self.get_disk_size()
        disk_params['diskType'] = disk_type
        disk_params['size'] = random.randint(1, disk_size)
        
        return disk_params

    def set_zdb_default_data(self, name=None, size='', mode="user"):

        zdb_params = {'name': name or self.random_string(),
                      'nodePort':  random.randint(600, 1000),
                      'mode': mode,
                      'sync': False,
                      'admin': '',
                      'namespaces': [],
                      'ztIdentity': '',
                      'nics': [],
                      'size': size
                      }
        disk_type = self.select_disk_type()
        zdb_path = self.get_disk_mount_path(disk_type)
        zdb_params['diskType'] = disk_type
        zdb_params["path"] = zdb_path       

        return zdb_params