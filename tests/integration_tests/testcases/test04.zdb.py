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
        pass

    def test001_create_zdb(self):
        """ SAL-001 Install zdb.

        **Test Scenario:**
        #. Create ZDB with default value, should succeed.
        #. Check that ZDB container created successfully with right data.
        """
        self.log("Create ZDB with default value, should succeed.")
        zdb_name = self.random_string
        zdb_data = self.set_zdb_default_data(name=zdb_name)
        zdb = self.zdb(node=self.node_sal, data=zdb_data)
        zdb.install()

        self.log("Check that ZDB container created successfully with right data.")
        containers = self.node_sal.client.container.list()
        zdb_container = [container for _ , container in containers.items() if container['container']['arguments']['name'] == zdb_name]
        self.assertTrue(zdb_container)
        self.assertIn(zdb_data["nodePort"], zdb_container["container"]["arguments"]["port"])

    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/143")
    def test002_create_more_than_one_zdb(self):
        """ SAL-001 Install zdb.

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
         self.assertIn('there is zdb with same name'.format(ns_name), e.exception.args[0])

        self.log("Create ZDB [zdb3] with same name but different port ,should fail.")
        zdb_data3 = self.set_zdb_default_data(name=zdb_name)
        zdb3 = self.zdb(node=self.node_sal, data=zdb_data3)
        created_zdb3 = zdb3._zerodb_sal
		with self.assertRaises(ValueError) as e:
            created_zdb3.deploy()
         self.assertIn('there is zdb with same name '.format(ns_name), e.exception.args[0])
