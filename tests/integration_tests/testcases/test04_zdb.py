from framework.base.zdb import ZDB
from testcases.base_test import BaseTest
from nose_parameterized import parameterized
import time
import unittest
import requests
import random
from framework.zdb_client import ZDBCLIENT


class ZDBTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.zdb_client = ZDBCLIENT(self.node_sal) 

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
        self.log("Create ZDB [ZDB1] with default value, should succeed.")
        zdb_name = self.random_string
        zdb_data = self.set_zdb_default_data(name=zdb_name)
        zdb = self.zdb(node=self.node_sal, data=zdb_data)
        zdb1_obj = zdb._zerodb_sal
        zdb1_obj.deploy()
        self.assertTrue(zdb1_obj.container.is_running())

        self.log("Create ZDB [zdb2] with same name and same port ,should fail.")
        zdb2 = self.zdb(node=self.node_sal, data=zdb_data)
        zdb2_object = zdb2._zerodb_sal
        with self.assertRaises(ValueError) as e:
            zdb2_object.deploy()
        self.assertIn('there is zdb with same name {}'.format(zdb_name), e.exception.args[0])

        self.log("Create ZDB [zdb3] with same name but different port ,should fail.")
        zdb_data3 = self.set_zdb_default_data(name=zdb_name)
        zdb3 = self.zdb(node=self.node_sal, data=zdb_data3)
        zdb3_object = zdb3._zerodb_sal
        
        with self.assertRaises(ValueError) as e:
            zdb3_object.deploy()
        self.assertIn('there is zdb with same name {} '.format(zdb_name), e.exception.args[0])


class ZDBActions(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        
        self.log("Create ZDB with default value, should succeed.")
        self.zdb_data = self.set_zdb_default_data()
        self.zdb = self.zdb(node=self.node_sal, data=self.zdb_data)
        self.zdb.install()
        self.zdb_client = ZDBCLIENT(self.node_ip, self.zdb._zerodb_sal.node_port) 
           
    def tearDown(self):
        pass

    def test001_ping_zdb(self):
        """ SAL-001 ping zdb server .

        **Test Scenario:**
        #. Create ZDB with default value and connect to it's client, should succeed.
        #. Ping zdb server with zdb client , should succeed.

        """
        self.log(". Ping Zdb server with zdb client , should succeed.")
        result = self.zdb_client.ping()
        self.assertEqual(result, "PONG")

    def test002_set_get(self):
        """ SAL-001 set and get key-value.

        **Test Scenario:**
        #. Set key [k1] with value[v1] ,should succeed.
        #. Get key [k1] value and check that it's the correct value, should succeed.
        #. Set key[k1] with different value, should succeed.
        #. Check that v1 updated with new value.

        """
        self.log("Set key [k1] with value[v1] ,should succeed.")
        key = self.random_string()
        value_1 = self.random_string()
        result = self.zdb_client.set(key, value_1)
        self.assertEqual(result, key)

        self.log("Get key [k1] value and check that it's the correct value, should succeed.")
        result_value = self.zdb_client.get(key)
        self.assertEqual(result_value, value_1)

        self.log("Set key[k1] with different value, should succeed.")
        value_2 = self.random_string()
        result = self.zdb_client.set(key, value_2)

        self.log("Check that v1 updated with new value.")
        result_value = self.zdb_client.get(key)
        self.assertEqual(result_value, value_2)
