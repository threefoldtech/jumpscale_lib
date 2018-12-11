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

    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/144")
    def test001_create_disk_with_wrong_data(self):
        """ SAl-024 create vdisk and attach it to deployed vm

        **Test Scenario:**

        #. Create zdb with default values.
        #. Create disk with worng filesystem, should fail.
        #. Create disk with large size, should fail.

        """
        self.log("Create zdb with default values.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdbs.append(zdb)

        self.log("Create disk with worng filesystem, should fail.")
        disk = Vdisk(node=self.node_sal, zdb=zdb.zerodb_sal)
        disk.data = self.set_vdisk_default_data()
        disk.data['filesystem'] = self.random_string()

        with self.assertRaises(RuntimeError) as e:
            disk.install()
        self.assertIn('Failed to create fs', e.exception.args[0])

        self.log("Create disk with large size, should fail.")
        disk.data = self.set_vdisk_default_data()
        disk.data['size'] = 10000000

        with self.assertRaises(RuntimeError) as e:
            disk.install()
        self.assertIn('Failed to create fs', e.exception.args[0])

    def test002_create_disk_with_exist_namespace_and_diff_size(self):
        """ SAl-025 create disk with exist namespace and different size

        **Test Scenario:**
        #. Create zdb with default values.
        #. Add namespace [ns] to zdb.
        #. Create disk using exist namespace [ns] with different size, should fail.
        #. Create disk using zdb and namespace wirh same size [ns], should succeed.

        """
        self.log("Create zdb with default values.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdbs.append(zdb)

        self.log("Add namespace to zdb.")
        ns_name = self.random_string()
        ns_size = random.randint(1, 50)
        zdb.namespace_create(name=ns_name, size=ns_size)

        self.log("Create disk using exist namespace [ns] with different size, should fail.")
        disk = Vdisk(node=self.node_sal, zdb=zdb.zerodb_sal)
        disk.data = self.set_vdisk_default_data(name=ns_name)

        with self.assertRaises(ValueError) as e:
            disk.install()
        self.assertIn('namespace with name {} already exists'.format(ns_name), e.exception.args[0])

        self.log("Create disk using using zdb and different namespace[ns1], should succeed.")
        disk.data['size'] = ns_size
        disk.install()

    @parameterized.expand(["deploy", "update"])
    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/102')
    def test003_attach_vdisk_to_vm(self, attach_by):
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

        if attach_by == "deploy":
            self.log("Attach disk [D1] to vm [VM1].")
            vm.add_disk(disk.disk)
            self.log("deploy vm [VM1].")
            vm.install()
        else:
            self.log("deploy vm [VM1].")
            vm.install()
            self.log("Attach disk [D1] to vm [VM1].")
            vm.add_disk(disk.disk)
            vm.update_disks()

        self.vms.append(vm.info()['uuid'])
        self.zdbs.append(zdb)

        self.log("Check that disk [D1] is attached to vm [VM1], should succeed.")
        disk_url = disk.get_url()
        self.assertEqual(vm.info()['params']['media'][0]['url'], disk_url)

        self.log("Remove the disk[D1] from the vm ,should succeed.")
        vm.remove_disk(disk.disk)
        vm.update_disks()
        self.assertFalse(vm.info()['params']['media'])
