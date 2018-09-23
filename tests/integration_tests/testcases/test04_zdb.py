from framework.base.zdb import ZDB
from testcases.base_test import BaseTest
from nose_parameterized import parameterized
import time
import unittest
import requests
import random

class ZDBTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        self.log('tear down zdbs')
        zdbs = self.node_sal.zerodbs.list()
        for zdb in zdbs:
            self.node_sal.primitives.drop_zerodb(zdb.name)

    def test001_create_zdb(self):
        """ SAL-027 Install zdb.

        **Test Scenario:**
        #. Create ZDB with default value, should succeed.
        #. Check that ZDB container created successfully with right data.
        """
        self.log("Create ZDB with default value, should succeed.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal, name=zdb_name)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()

        self.log("Check that ZDB container created successfully with right data.")
        containers = self.node_sal.client.container.list()
        zdb_container = [container for _ , container in containers.items() if container['container']['arguments']['name'] == zdb_name]
        self.assertTrue(zdb_container)
        self.assertIn(str(zdb.data["nodePort"]), zdb_container[0]["container"]["arguments"]["port"])

    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/143")
    def test002_create_more_than_one_zdb(self):
        """ SAL-028 Install more than one zdb.

        **Test Scenario:**
        #. Create ZDB [zdb1] with default value, should succeed.
        #. Create ZDB [zdb2] with same name and same port ,should fail.
        #. Create ZDB [zdb3] with same name but different port ,should fail .
        """
        self.log("Create ZDB with default value, should succeed.")
        zdb_name = self.random_string
        zdb_data = self.set_zdb_default_data(name=zdb_name)
        zdb = self.zdb(node=self.node_sal, data=zdb_data)
        created_zdb = zdb._zerodb_sal
        created_zdb.deploy()
        self.assertTrue(created_zdb.container.is_running())

        self.log("Create ZDB [zdb2] with same name and same port ,should fail.")
        zdb2 = self.zdb(node=self.node_sal, data=zdb_data)
        created_zdb2 = zdb2._zerodb_sal

        with self.assertRaises(ValueError) as e:
             created_zdb2.deploy()
        self.assertIn('there is zdb with same name {}'.format(zdb_name), e.exception.args[0])

        self.log("Create ZDB [zdb3] with same name but different port ,should fail.")
        zdb_data3 = self.set_zdb_default_data(name=zdb_name)
        zdb3 = self.zdb(node=self.node_sal, data=zdb_data3)
        created_zdb3 = zdb3._zerodb_sal

        with self.assertRaises(ValueError) as e:
            created_zdb3.deploy()
        self.assertIn('there is zdb with same name {}'.format(zdb_name), e.exception.args[0])

    def test003_start_stop_zdb(self):
        """ SAL-029 start and stop zdb

        **Test Scenario:**
        #. Create ZDB [zdb1] with default value, should succeed.
        #. Check that zdb is running.
        #. Stop zdb and check that zdb is stopped.
        #. Start it again and check that it becomes running again. 

        """
        self.log("Create ZDB [zdb1] with default value, should succeed.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal, name=zdb_name)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()

        import ipdb; ipdb.set_trace()
        self.log("Check that zdb is running.")
        self.assertTrue(zdb._zerodb_sal.is_running()[0])

        self.log("Stop zdb and check that zdb is stopped.")
        zdb.stop()
        self.assertFalse(zdb._zerodb_sal.is_running()[0])

        self.log("Start it again and check that it becomes running again")
        zdb.start()
        self.assertTrue(zdb._zerodb_sal.is_running()[0])

    def test004_add_remove_namespace_to_zdb(self):
        """ SAL-030 create zdb and add/remove namespace.

        **Test Scenario:**
        #. Create ZDB [zdb1] with default value, should succeed.
        #. Add namespace [ns1] to zdb, should succeed.
        #. Check that namespace added successfully. 
        #. Remove namespace [ns1], should succeed.

        """
        self.log("Create ZDB [zdb1] with default value, should succeed.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal, name=zdb_name)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        import ipdb; ipdb.set_trace()

        self.log("Add namespace [ns1] to zdb, should succeed.")
        ns_name = self.random_string()
        ns_size = random.randint(1, 50)
        zdb.namespace_create(name=ns_name, size=ns_size)

        self.log("Check that namespace added successfully.")
        self.assertEqual(zdb._zerodb_sal.to_dict()['namespaces'][0]['name'], ns_name) 
        self.assertEqual(zdb._zerodb_sal.to_dict()['namespaces'][0]['size'], ns_size)

        self.log("Remove namespace [ns1], should succeed.")
        zdb.namespace_delete(ns_name)
        self.assertFalse(zdb._zerodb_sal.to_dict()['namespaces'])

    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/144')
    def test005_add_namespace_to_zdb(self):
        """ SAL-031 create zdb and add namespace.

        **Test Scenario:**
        #. Create ZDB [zdb1] with default value, should succeed.
        #. Add namespace [ns1] to zdb, should succeed.
        #. Add namespace with same name as [ns1], should fail.
        #. Add namespace without size, should fail. 
        #. Add namespace large size, should fail. 

        """
        self.log("Create ZDB [zdb1] with default value, should succeed.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal, name=zdb_name)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()

        self.log("Add namespace [ns1] to zdb, should succeed.")
        ns_name = self.random_string()
        ns_size = random.randint(1, 50)
        zdb.namespace_create(name=ns_name, size=ns_size)

        self.log("Add namespace with same name as [ns1], should fail.")
        with self.assertRaises(ValueError) as e:
            zdb.namespace_create(name=ns_name, size=ns_size)
        self.assertIn('Namespace {} already exists'.format(ns_name), e.exception.args[0])

        self.log("Add namespace without size, should fail.")
        # should fail 
        ns_name1 = self.random_string()
        with self.assertRaises(ValueError) as e:
            zdb.namespace_create(name=ns_name1)
        self.assertIn('size error', e.exception.args[0])

        self.log("Add namespace large size, should fail.")
        #should fail
        ns_name2 = self.random_string()
        with self.assertRaises(ValueError) as e:
            zdb.namespace_create(name=ns_name2, size=1000000000)
        self.assertIn('size error', e.exception.args[0])