from framework.base.zdb import ZDB
from testcases.base_test import BaseTest
from nose_parameterized import parameterized
import time
import unittest
import requests
import random
from framework.zdb_client import ZDBCLIENT
from jumpscale import j

class ZDBTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        self.log('tear down zdbs')
        for zdb in self.zdbs:
            namespaces = zdb.namespace_list()
            for namespace in namespaces:
                zdb.namespace_delete(namespace.name)
            self.node_sal.client.container.terminate(zdb.container.id)
        self.zdbs.clear()

    def test001_create_zdb(self):
        """ SAL-027 Install zdb.
        **Test Scenario:**
        #. Create ZDB with default value, should succeed.
        #. Check that ZDB container created successfully with right data.
        #. Check that ZDB created using zdb client.
        """
        self.log("Create ZDB with default value, should succeed.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdb_cont_ids.append(zdb.zerodb_sal)

        self.log("Check that ZDB container created successfully with right data.")
        containers = self.node_sal.client.container.list()
        zdb_container = [container for _ , container in containers.items() if container['container']['arguments']['name'] == zdb_name]
        self.assertTrue(zdb_container)
        self.assertIn(str(zdb.data["nodePort"]), zdb_container[0]["container"]["arguments"]["port"])
        
        self.log("Check that ZDB created using zdb client.")
        zdb_client = ZDBCLIENT(self.node_ip, zdb.zerodb_sal.node_port)
        result = zdb_client.ping("lower")
        self.assertEqual(result, "PONG")

    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/143")
    def test002_create_more_than_one_zdb(self):
        """ SAL-028 Install more than one zdb.
        **Test Scenario:**
        #. Create ZDB [zdb1] with default value, should succeed.
        #. Create ZDB [zdb2] with same name and same port ,should fail.
        #. Create ZDB [zdb3] with same name but different port ,should fail.
        """
        self.log("Create ZDB with default value, should succeed.")
        zdb_name = self.random_string()
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdb_cont_ids.append(zdb.zerodb_sal)

        self.log("Create ZDB [zdb2] with same name and same port ,should fail.")
        zdb2 = self.zdb(node=self.node_sal, data=zdb.data)
        zdb2.install()

        with self.assertRaises(ValueError) as e:
            zdb2.install()
        self.assertIn('there is zdb with same name {}'.format(zdb_name), e.exception.args[0])

        self.log("Create ZDB [zdb3] with same name but different port ,should fail.")
        zdb3 = self.zdb(node=self.node_sal)
        zdb3.data = self.set_zdb_default_data(name=zdb_name)

        with self.assertRaises(ValueError) as e:
            zdb2.install()
        self.assertIn('there is zdb with same name {}'.format(zdb_name), e.exception.args[0])
    
    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/159')
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
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdb_cont_ids.append(zdb.zerodb_sal)
    
        self.log("Check that zdb is running.")
        self.assertTrue(zdb.zerodb_sal.is_running()[0])
        zdb_client = ZDBCLIENT(self.node_ip, zdb.zerodb_sal.node_port)
        result = zdb_client.ping("lower")
        self.assertEqual(result, "PONG")

        self.log("Stop zdb and check that zdb is stopped.")
        zdb.stop()

        self.assertFalse(zdb.zerodb_sal.is_running()[0])
        with self.assertRaises(Exception):
            result = zdb_client.ping("lower")
        
        self.log("Start it again and check that it becomes running again")
        zdb.start()
        self.assertTrue(zdb.zerodb_sal.is_running()[0])
        result = zdb_client.ping("lower")
        self.assertEqual(result, "PONG")
        
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
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdb_cont_ids.append(zdb.zerodb_sal)
        zdb_client = ZDBCLIENT(self.node_ip, zdb.zerodb_sal.node_port)

        self.log("Add namespace [ns1] to zdb, should succeed.")
        ns_name = self.random_string()
        disk_size = self.get_most_free_disk_type_size()[1]
        ns_size = random.randint(1, disk_size)
        zdb.namespace_create(name=ns_name, size=ns_size)

        self.log("Check that namespace added successfully.")
        self.assertEqual(zdb.zerodb_sal.to_dict()['namespaces'][0]['name'], ns_name) 
        self.assertEqual(zdb.zerodb_sal.to_dict()['namespaces'][0]['size'], ns_size)
        result = zdb_client.nslist("lower")
        self.assertIn(ns_name, result)

        self.log("Remove namespace [ns1], should succeed.")
        zdb.namespace_delete(ns_name)
        self.assertFalse(zdb.zerodb_sal.to_dict()['namespaces'])
        result = zdb_client.nslist("lower")
        self.assertNotIn(ns_name, result)

    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/144')
    def test005_add_namespaces_to_zdb(self):
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
        zdb = self.zdb(node=self.node_sal)
        zdb.data = self.set_zdb_default_data(name=zdb_name)
        zdb.install()
        self.zdb_cont_ids.append(zdb.zerodb_sal)

        self.log("Add namespace [ns1] to zdb, should succeed.")
        ns_name = self.random_string()
        disk_size = self.get_most_free_disk_type_size()[1]
        ns_size = random.randint(1, disk_size)
        zdb.namespace_create(name=ns_name, size=ns_size)

        self.log("Add namespace with same name as [ns1], should fail.")
        with self.assertRaises(ValueError) as e:
            zdb.namespace_create(name=ns_name, size=ns_size)
        self.assertIn('Namespace {} already exists'.format(ns_name), e.exception.args[0])

        self.log("Add namespace without size, should fail.")
        ns_name1 = self.random_string()
        with self.assertRaises(ValueError) as e:
            zdb.namespace_create(name=ns_name1)
        self.assertIn('size error', e.exception.args[0])

        self.log("Add namespace large size, should fail.")
        ns_name2 = self.random_string()
        ns_size2 = random.randint(1000000000, 9000000000)
        with self.assertRaises(ValueError) as e:
            zdb.namespace_create(name=ns_name2, size=ns_size2)
        self.assertIn('size error', e.exception.args[0])

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
        self.zdb_cont_ids.append(self.zdb.zerodb_sal)
        self.zdb_client = ZDBCLIENT(self.node_ip, self.zdb.zerodb_sal.node_port) 
           
    def tearDown(self):
        self.log('tear down zdbs')
        for zdb in self.zdbs:
            namespaces = zdb.namespace_list()
            for namespace in namespaces:
                zdb.namespace_delete(namespace.name)
            self.node_sal.client.container.terminate(zdb.container.id)
        self.zdbs.clear()

    @parameterized.expand(["upper", "lower"])
    def test001_ping_zdb(self, case):
        """ SAL-032 ping zdb server .

        **Test Scenario:**
        #. Create ZDB with default value and connect to it's client, should succeed.
        #. Ping zdb server with zdb client , should succeed.

        """
        if case == "upper":
            self.skipTest("PING return True")

        self.log(". Ping Zdb server with zdb client , should succeed.")
        result = self.zdb_client.ping(case)
        self.assertEqual(result, "PONG")

    @parameterized.expand(["upper", "lower"])
    def test002_set_get_key(self,case):
        """ SAL-033 set and get key-value.

        **Test Scenario:**
        #. Set key [k1] with value[v1], should succeed.
        #. Get key [k1] value and check that it's the correct value, should succeed.
        #. Set key [k1] with different value, should succeed.
        #. Check that v1 updated with new value.

        """
        self.log("Set key [k1] with value[v1] ,should succeed.")
        key = self.random_string()
        value_1 = self.random_string()
        result = self.zdb_client.set(key, value_1, case)
        self.assertEqual(result, key)

        self.log("Get key [k1] value and check that it's the correct value, should succeed.")
        result_value = self.zdb_client.get(key, case)
        self.assertEqual(result_value, value_1)

        self.log("Set key[k1] with different value, should succeed.")
        value_2 = self.random_string()
        result = self.zdb_client.set(key, value_2, case)
        
        self.log("Check that v1 updated with new value.")
        result_value = self.zdb_client.get(key, case)
        self.assertEqual(result_value, value_2)

    @parameterized.expand(["upper", "lower"])
    def test003_exists_delete_key(self, case):
        """ SAL-034 check key exists and then deletes it. 

        **Test Scenario:**
        #. Set key [k1] with value[v1], should succeed.
        #. Check that key is exist. 
        #. Delete the key.
        #. Check that key is not exist. 

        """
        self.log("Set key [k1] with value[v1] ,should succeed.")
        key = self.random_string()
        value_1 = self.random_string()
        result = self.zdb_client.set(key, value_1, case)
        self.assertEqual(result, key)

        self.log("Check that key is exist.")
        result = self.zdb_client.exists(key, case)
        self.assertEqual(result, 1)

        self.log("Delete the key.")
        self.zdb_client.delete(key, case)

        self.log("Check that key is not exist.")
        result = self.zdb_client.exists(key, case)
        self.assertEqual(result, 0)

    @parameterized.expand(["upper", "lower"])
    def test004_create_delete_namespace(self, case):
        """ SAL-035 create namespace using zdb client.

        **Test Scenario:**
        #. Create namespace using zdb client.
        #. Check that namespace created using zdb client. 
        #. Delete namespace using zdb client. 
        #. Check that namespace deleted. 

        """
        self.log("Create namespace using sal.")
        ns_name = self.random_string()
        self.zdb_client.nsnew(namespace=ns_name, case=case)

        self.log("Check that namespace created using zdb client.")
        result = self.zdb_client.nslist(case)
        self.assertIn(ns_name, result)

        self.log("Delete namespace using sal client. ")
        self.zdb_client.nsdel(namespace=ns_name, case=case)

        self.log("Check that namespace deleted.")
        result = self.zdb_client.nslist(case)
        self.assertNotIn(ns_name, result)

    @parameterized.expand([["maxsize", "upper"], ["maxsize", "lower"], ["password", "upper"], ["password", "lower"], ["public", "upper"], ["public", "lower"]])
    def test005_change_namespace_property(self, prop, case):
        """ SAL-036 change namespace property. 

        **Test Scenario:**
        #. Create namespace.
        #. Change namespace property.
        #. Check that it is changed using zdb client, should succeed.
        """
        self.log("Create namespace using sal.")
        ns_name = self.random_string()
        disk_size = self.get_most_free_disk_type_size()[1]
        ns_size = random.randint(1, disk_size)
        self.zdb.namespace_create(name=ns_name, size=ns_size)

        if prop == "maxsize":
            prop_value = random.randint(1, disk_size)
            search = "data_limits_bytes"
            check = str(prop_value)

        elif prop == "password":
            prop_value = j.data.idgenerator.generateXCharID(25)
            search = "password"
            check = 'yes'

        else:
            prop_value = False
            search = "public"
            check = 'no'

        self.log("Change namespace property.")
        self.zdb.namespace_set(ns_name, prop, prop_value)

        self.log(" Check that it is changed using zdb client, should succeed.")
        result = self.zdb_client.nsinfo(ns_name, case)
        result = result[result.find(':',result.find(search)) + 2 : result.find('\n', result.find(search))]
        self.assertEqual(result, check)
    
    @parameterized.expand(["upper", "lower"])
    def test006_set_password_select_namespace(self, case):
        """ SAL-037 create namespace using zdb client.

        **Test Scenario:**
        #. Create namespace using zdb client.
        #. Set password to namespace. 
        #. Select the namespace with wrong password, should fails.
        #. Select the namespace with right password, should succeed. 

        """
        self.log("Create namespace using sal.")
        ns_name = self.random_string()
        self.zdb_client.nsnew(namespace=ns_name, case=case)

        self.log("Set password to namespace.")
        password = j.data.idgenerator.generateXCharID(10)
        self.zdb_client.nsset(namespace=ns_name, property='password', value=password, case=case)

        self.log("Select the namespace with wrong password, should fails.")
        worng_password = j.data.idgenerator.generateXCharID(10)
        with self.assertRaises(Exception) as e:
            result = self.zdb_client.select(namespace=ns_name, password=worng_password, case=case)
        self.assertIn('Access denied', e.exception.args[0])

        self.log("Select the namespace with right password, should succeed.")
        result = self.zdb_client.select(namespace=ns_name, password=password, case=case)
        self.assertEqual(result, 'OK')
