from framework.base.vdisk import Vdisk
from framework.base.zdb import ZDB
from framework.base.vms import VM
from testcases.base_test import BaseTest
from nose_parameterized import parameterized
import multiprocessing
import time
import unittest
import requests
import random
import subprocess


class Vdisktest(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.log("Create zdb with default values.")
        zdb_name = self.random_string()
        self.zdb = self.zdb(node=self.node_sal)
        self.zdb.data = self.set_zdb_default_data(name=zdb_name)
        self.zdb.install()
        self.zdbs.append(self.zdb)

        self.log("Create disk [D1] with default data")
        self.disk = Vdisk(node=self.node_sal, zdb=self.zdb.zerodb_sal)
        self.disk.data = self.set_vdisk_default_data()
        self.mount_path = '/mnt/{}'.format(self.random_string())
        new_data = {'mountPoint': self.mount_path, 'filesystem': 'ext4'}
        self.update_default_data(self.disk.data, new_data)
        self.disk.install()

        self.log("Create vm [VM1] with default values, should succeed.")
        self.vm = self.vm(node=self.node_sal)
        self.vm.data = self.set_vm_default_values(os_type="ubuntu")

        self.log("Update default data by adding type default nics")
        network_name = self.random_string()
        nics = {'nics': [{'name': network_name, 'type': 'default'}]}
        self.vm.data = self.update_default_data(self.vm.data, nics)
        self.vm.generate_vm_sal()

        self.log(" Add zerotier network to VM1, should succeed.")
        self.vm.add_zerotier_nics(network=self.zt_network)

        self.log("Attach disk [D1] to vm [VM1].")
        self.vm.add_disk(self.disk.disk)

    def tearDown(self):
        self.log('tear down vms')
        for uuid in self.vms:
            self.node_sal.client.kvm.destroy(uuid)
        self.vms.clear()

        self.log('tear down zdbs')
        for zdb in self.zdbs:
            namespaces = zdb.namespace_list()
            for namespace in namespaces:
                zdb.namespace_delete(namespace.name)
            self.node_sal.client.container.terminate(zdb.zerodb_sal.container.id)
        self.zdbs.clear()

    def read_write_file(self, mount_path, guest_port, vm_zt_ip, i, result_dict):
        self.log("Download specific file with size 10M to vm[VM1].")
        file_name = self.random_string()
        cmd = 'cd {}; wget https://github.com/AhmedHanafy725/test/raw/master/test_file -O {}'.format(
            mount_path, file_name)
        self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd=cmd)

        self.log("Get file md5 of the downloaded file.")
        cmd = 'cd {}; md5sum {}'.format(mount_path, file_name)
        result1 = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd=cmd)
        result1 = result1[:result1.find(' ')]

        self.log("Download this file from [VM1] to the test machine through the server[S1].")
        cmd = 'wget http://{}:{}/{}'.format(vm_zt_ip, guest_port, file_name)
        response = subprocess.run(cmd, shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertFalse(response.returncode)

        self.log("Get file md5 of the downloaded file.")
        cmd = 'md5sum {}'.format(file_name)
        response = subprocess.run(cmd, shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result2 = response.stdout.strip()
        result2 = result2[:result2.find(' ')]

        self.log("remove downloaded files")
        cmd = 'rm -f  {}'.format(file_name)
        response = subprocess.run(cmd, shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertFalse(response.returncode)

        result_dict[i] = (result1, result2)

    def test001_read_and_write_file_from_vdisk(self):
        """ SAL-040 read and write several file at same time.

        **Test Scenario:**

        #. Create zdb with default data.
        #. Create disk [D1] with default data.
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Attach disk [D1] to vm [VM1].
        #. Add port to create server on it.
        #. Create server[S1], should succeed.
        #. Do this steps five times using multiprocessing:
        #. Download specific file with size 10M to vm[VM1].
        #. Get file md5 of the downloaded file.
        #. Download this file from [VM1] to the test machine through the server[S1].
        #. Get file md5 of the downloaded file.
        #. Then download the same to the test machine.
        #. Check md5 of the those three files, should be the same.

        """
        self.log("Add port to create server on it.")
        port_name = self.random_string()
        host_port = random.randint(3000, 4000)
        guest_port = random.randint(5000, 6000)
        self.vm.add_port(name=port_name, source=host_port, target=guest_port)

        self.log("deploy vm [VM1].")
        self.vm.install()
        self.vms.append(self.vm.info()['uuid'])

        self.log("get ztIdentity and vm ip")
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_zerotier_ip(ztIdentity)

        self.log("create server on the vm at port {}.".format(guest_port))
        cmd = 'cd {}; python3 -m http.server {} &> /tmp/server.log &'.format(self.mount_path, guest_port)
        self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd=cmd)
        time.sleep(10)

        self.log("Create dict to get data from multiprocess")
        manager = multiprocessing.Manager()
        result_dict = manager.dict()
        jobs = []

        for i in range(5):
            process = multiprocessing.Process(target=self.read_write_file, args=(
                self.mount_path, guest_port, vm_zt_ip, i, result_dict))
            jobs.append(process)
            process.start()

        self.log("wait till all processes finish")
        for proc in jobs:
            proc.join()

        self.log("Download the same to the test machine.")
        file_name2 = self.random_string()
        cmd = 'wget https://github.com/AhmedHanafy725/test/raw/master/test_file -O {}'.format(file_name2)
        response = subprocess.run(cmd, shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertFalse(response.returncode)

        cmd = 'md5sum {}'.format(file_name2)
        response = subprocess.run(cmd, shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = response.stdout.strip()
        result = result[:result.find(' ')]

        self.log("remove downoaded file")
        cmd = 'rm -f {}'.format(file_name2)
        response = subprocess.run(cmd, shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertFalse(response.returncode)

        self.log("Check md5 of the those three files, should be the same")
        for i in range(5):
            self.assertEqual(result_dict[i][0], result)
            self.assertEqual(result_dict[i][1], result)

    @parameterized.expand(['namespace', 'zdb'])
    def test002_delete_namespace_or_stop_zdb_of_vdisk(self, delete):
        """ SAL-041 delete namespace or stop zdb of vdisk.

        **Test Scenario:**

        #. Create disk [D1] with default data.
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Attach disk [D1] to vm [VM1].
        #. Try to write on disk mounting point, should succeed.
        #. (Delete namespace/ stop zdb) and try to write again, should fail.
        """
        self.log("deploy vm [VM1].")
        self.vm.install()
        self.vms.append(self.vm.info()['uuid'])
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_zerotier_ip(ztIdentity)

        self.log("Try to write on disk mounting point, should succeed.")
        file_name = self.random_string()
        content = self.random_string()
        cmd = 'echo {} > {}/{}'.format(content, self.mount_path, file_name)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd=cmd)

        cmd = 'cat {}/{}'.format(self.mount_path, file_name)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd=cmd)
        self.assertEqual(result, content)

        self.log("(Delete namespace /stop zdb) and try to write again, should fail.")
        if delete == 'zdb':
            self.zdb.stop()
        else:
            self.zdb.namespace_delete(self.disk.data['name'])
        time.sleep(30)

        cmd = 'echo {} > {}/{}'.format(self.random_string(), self.mount_path, self.random_string())
        result = self.execute_command(ip=vm_zt_ip, cmd=cmd)
        self.assertTrue(result.returncode)
