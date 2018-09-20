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
        vms = self.node_sal.client.kvm.list()
        for vm in vms:
            self.node_sal.client.kvm.destroy(vm['uuid'])

        self.log('tear down zdbs')
        zdbs = self.node_sal.zerodbs.list()
        for zdb in zdbs:
            self.node_sal.primitives.drop_zerodb(zdb.name)
    
    def test001_create_disk_with_wrong_data(self):
        """ SAl-024 create vdisk and attach it to deployed vm

        **Test Scenario:**

        #. Create disk using non-valid data (worng filesystem), should fail.
        #. Create disk using non-valid data (big size), should fail.
        #. Create disk using exist namespace and has different size, should fail.
        #. Create disk using using zdb[zdb1] and namespace[ns1], should succeed.
                
        """
        self.log("Create disk [D1] using non-valid data (worng filesystem), should fail.")
        disk = Vdisk(node=self.node_sal)
        disk.data = self.set_vdisk_default_data()
        disk.data['filesystem'] = self.random_string()

        self.log("Create disk using non-valid data (worng filesystem), should fail.")
        with self.assertRaises(RuntimeError) as e:
            disk.install()
        self.assertIn('Failed to create fs', e.exception.args[0])
        
        # issue ('https://github.com/threefoldtech/jumpscale_lib/issues/144')
        # self.log("Create disk using non-valid data (big size), should fail.")
        # disk.data = self.set_vdisk_default_data()
        # disk.data['size'] = 100000000

        # with self.assertRaises(RuntimeError) as e:
        #     disk.install()
        # self.assertIn('Failed to create fs', e.exception.args[0])

        self.log("Create disk using exist namespace and has different size, should fail.")
        ns_name = self.random_string()
        ns_size = random.randint(1, 100)
        disk.data = self.set_vdisk_default_data(name=ns_name)
        disk.zdb.namespaces.add(name=ns_name, size=ns_size)

        with self.assertRaises(ValueError) as e:
            disk.install()
        self.assertIn('namespace with name {} already exists'.format(ns_name), e.exception.args[0])

        self.log("Create disk using using zdb[zdb1] and namespace[ns1], should succeed.")
        disk.data = self.set_vdisk_default_data()
        disk.install()

    def test002_attach_vdisk_to_vm(self):
        """ SAL-025 create vdisk and attach it to vm.

        **Test Scenario:**

        #. Create disk [D1] with default data.
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Attach disk [D1] to vm [VM1].
        #. deploy vm [VM1].
        #. Check that disk [D1] is attached to vm [VM1], should succeed.

        """
        self.log("Create disk [D1] with default data")
        disk = Vdisk(node=self.node_sal)
        disk.data = self.set_vdisk_default_data()
        disk.install()

        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)
        
        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(created_vm)

        self.log("Attach disk [D1] to vm [VM1].")
        created_vm.disks.add(disk.disk)

        self.log("deploy vm [VM1].")
        vm.install(created_vm)

        self.log("Check that disk [D1] is attached to vm [VM1], should succeed.")
        self.assertTrue(created_vm.info['params']['media'])

    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/141')
    def test003_attach_vdisk_to_deployed_vm(self):
        """ SAl-026 create vdisk and attach it to deployed vm

        **Test Scenario:**

        #. create disk [D1] with default data.
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. deploy vm [VM1].
        #. Attach disk [D1] to vm [VM1].
        #. Check that disk [D1] is attached to vm [VM1], should succeed.
    
        """
        self.log("Create disk [D1] with default data")
        disk = Vdisk(node=self.node_sal)
        disk.data = self.set_vdisk_default_data()
        disk.install()    

        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)
        
        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(created_vm)

        self.log("deploy vm [VM1].")
        vm.install(created_vm)

        self.log("Attach disk [D1] to vm [VM1].")
        created_vm.disks.add(disk.disk)
        created_vm.update_disks()

        self.log("Check that disk [D1] is attached to vm [VM1], should succeed.")
        self.assertTrue(created_vm.info['params']['media'])
