from framework.base.vdisk import Vdisk
from framework.base.zdb import ZDB
from framework.base.vms import VM
from testcases.base_test import BaseTest
from nose_parameterized import parameterized
import time
import unittest
import requests
import random

class Vdisktest(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
    
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

    def test001_attach_vdisk_to_vm(self):
        """ SAL-026 create vdisk and attach it to vm.

        **Test Scenario:**

        #. Create disk [D1] with default data.
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Attach disk [D1] to vm [VM1].
        #. deploy vm [VM1].
        #. Check that disk [D1] is attached to vm [VM1], should succeed.
        #. Remove the disk[D1] from the vm ,should succeed.

        """
        self.log("Create zdb with default values.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdbs.append(zdb)

        self.log("Create disk [D1] with default data")
        disk = Vdisk(node=self.node_sal, zdb=zdb.zerodb_sal)
        disk.data = self.set_vdisk_default_data()
        disk.install()

        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        vm.generate_vm_sal()

        self.log(" Add zerotier network to VM1, should succeed.")
        vm.add_zerotier_nics(network=self.zt_network)
        
        self.log("Attach disk [D1] to vm [VM1].")
        vm.add_disk(disk.disk, mountpoint='/mnt/hamada', filesystem='ext4', label='sba7o')
        self.log("deploy vm [VM1].")
        vm.install()

        ztIdentity = vm.data["ztIdentity"]
        vm_zt_ip = self.get_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertEqual(result, '/root')

        import ipdb; ipdb.set_trace()
        self.vms.append(vm.info()['uuid'])
        self.zdbs.append(zdb)

        

    def test002_attach_vdisk_to_vm(self):
        """ SAL-026 create vdisk and attach it to vm.

        **Test Scenario:**

        #. Create disk [D1] with default data.
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Attach disk [D1] to vm [VM1].
        #. deploy vm [VM1].
        #. Check that disk [D1] is attached to vm [VM1], should succeed.
        #. Remove the disk[D1] from the vm ,should succeed.

        """
        self.log("Create zdb with default values.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdbs.append(zdb)

        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        vm.generate_vm_sal()

        for _ in range(10):
            self.log("Create disk [D1] with default data")
            disk = Vdisk(node=self.node_sal, zdb=zdb.zerodb_sal)
            disk.data = self.set_vdisk_default_data()
            disk.install()

            dir_name = self.random_string()
            label = self.random_string()
            self.log("Attach disk [D1] to vm [VM1].")
            vm.add_disk(disk.disk, mountpoint='/mnt/{}'.format(dir_name), filesystem='ext4', label=label)
        

        self.log(" Add zerotier network to VM1, should succeed.")
        vm.add_zerotier_nics(network=self.zt_network)
        
        
        self.log("deploy vm [VM1].")
        vm.install()

        ztIdentity = vm.data["ztIdentity"]
        vm_zt_ip = self.get_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertEqual(result, '/root')

        import ipdb; ipdb.set_trace()
        self.vms.append(vm.info()['uuid'])
        self.zdbs.append(zdb)