from testcases.base_test import BaseTest
from nose_parameterized import parameterized
from termcolor import colored
import unittest
import time
import random, requests

class GWTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.gateway = self.gw(node=self.node_sal)
        self.gateway.data = self.set_gw_default_values()
        self.vm_data = self.set_vm_default_values(os_type="ubuntu")
        self.vm = self.vm(node=self.node_sal, data=self.vm_data)

    def tearDown(self):
        self.log("destroy created gateway")
        self.gateway.destroy()

        self.log("destroy created vms.")
        for uuid in self.vms:
            self.node_sal.client.kvm.destroy(uuid)
        self.vms.clear()


    def test001_deploy_getway_without_public_network(self):
        """SAL-GW-011
        *Test case for deploying gateway without default public network .
        Test Scenario:

        #. Create gateways[GW1] without network interface, should succeed.
        #. Deploy [GW1], should fail as there is no public network.
        """
        self.log(" Deploy [GW1], should fail .")
        with self.assertRaises(RuntimeError) as e:
            self.gateway.install()
        self.assertIn("Need exactly one public network", e.exception.args[0])

    def test002_deploy_getway_with_public_network(self):
        """SAL-GW-012
        *Test case for deploying gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1], should succeed.
        #. Attach default network to [GW1] and don't set network public to True .
        #. Deploy [GW1], should fail ,need at least one public network.
        #. Set network public to True.
        #. Deploy [GW1], should succeed.
        """
        self.log("Create gateways[GW1], should succeed.")
        self.gateway.generate_gw_sal()

        self.log("Attach default network to [GW1] and don't set network public to True .")
        network = self.gateway.add_network(name="public", type_="default")

        self.log("Deploy [GW1], should fail ,need at least one public network.")
        with self.assertRaises(RuntimeError) as e:
            self.gateway.install()
        self.assertIn("Need exactly one public network", e.exception.args[0])

        self.log("Set network public to True.")
        network.public = True

        self.log("Deploy [GW1], should succeed.")
        self.gateway.install()

    def test003_add_network_name_exist(self):
        """SAL-GW-013
        *Test case for deploying gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1], should succeed.
        #. Add network [N1] to [GW1], should succeed.
        #. Add network [N2] with same type and same name as [N1] to [GW1],should fail .
        #. Add network [N3] with different type and same name as [N1] to [GW1],should fail .
        """
        self.gateway.generate_gw_sal()

        self.log(" Add network [N1] to [GW1], should succeed.")
        network_name = 'n'+self.random_string()
        network = self.gateway.add_network(name=network_name, type_="default")
        network.public = True
        self.gateway.install()

        self.log("Add network [N2] with same type and same name as [N1] to [GW1],should fail .")
        
        with self.assertRaises(ValueError) as e:
            self.gateway.add_network(name=network_name, type_="default")
        self.assertIn("Element with name %s already exists"%network_name, e.exception.args[0])

        self.log("Add network [N2] with different type and same name as [N1] to [GW1],should fail .")
        with self.assertRaises(ValueError) as e:
            self.gateway.add_network(name=network_name, type_="zerotier", networkid=self.zt_network.id)
        self.assertIn("Element with name %s already exists"%network_name, e.exception.args[0])

    def test004_remove_network(self):
        """SAL-GW-014
        *Test case for deploying gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1], should succeed.
        #. Add network [N1] to [GW1], should succeed.
        #. Deploy [GW1], should succeed.
        #. Remove N1, should succeed. 
        #. Check that network has been removed.
        """

        self.gateway.generate_gw_sal()
        self.log("Add network [N1] to [GW1], should succeed.")
        network_name = 'n'+self.random_string()
        created_network = self.gateway.add_network(name=network_name, type_="default")        
        created_network.public = True
    
        self.log("Deploy [GW1], should succeed.")
        self.gateway.install()
        
        self.log("remove N1, should succeed.")
        self.gateway.remove_network(created_network)

        self.log("Check that network has been removed.")
        self.assertFalse(self.gateway.list_network())
        with self.assertRaises(RuntimeError) as e:
            self.gateway.install()
        self.assertIn("Need exactly one public network", e.exception.args[0])

    def test005_deploy_getways_with_public_network(self):
        """SAL-GW-015
        *Test case for deploying more than one gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1],[GW2], should succeed.
        #. Attach default network to [GW1] and [GW2] ,then set network public to True .
        #. Deploy [GW1], should succeed
        #. Deploy [GW2], should fail as we can create only one gateway with type defaulgt public network.
        """
        self.log("Create gateways[GW1],[GW2], should succeed.")
        gw2_data = self.set_gw_default_values()
        self.gateway2 = self.gw(node=self.node_sal, data=gw2_data)
        self.gateway.generate_gw_sal()
        self.gateway2.generate_gw_sal()

        self.log("Attach default network to [GW1] and [GW2] ,then set network public to True.")
        network1 = self.gateway.add_network(name="public", type_="default")
        network1.public = True
        network2 = self.gateway2.add_network(name="public", type_="default")
        network2.public = True

        self.log(" Deploy [GW1], should succeed")
        self.gateway.install()

        self.log("Deploy [GW2], should fail as we can create only one gateway with type default public network.")
        with self.assertRaises(RuntimeError) as e:
            self.gateway2.install()
        self.assertIn("port already in use", e.exception.args[0])

    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/132")
    def test06_create_gateway_with_public_and_zerotier_vm(self):
        """SAL-GW-016
        *Test case for deploying gateways with public and zerotier networks. *
        Test Scenario:

        #. Create gateway with public default network, should succeed.
        #. Add zerotier network as private network, should succeed.
        #. Adding a new vm t to gateway private network , should succeed.
        #. Check that the vm has been join the zerotier network.
        """
        self.gateway.generate_gw_sal()
        self.log("Create gateway with public default network, should succeed.")
        network_name = self.random_string()
        created_network = self.gateway.add_networks(name=network_name, type_="default")        
        created_network.public = True

        self.log("Add zerotier network as private network, should succeed.")
        zt_network = self.gateway.add_zerotier(self.zt_network)

        self.log("Adding a new vm t to gateway private network , should succeed.")
        self.vm.install()
        self.vms.append(self.vm.info()['uuid'])
        zt_network.hosts.add(self.vm.vm_sal)
        self.gateway.install()
        self.vm.install()

        self.log("Check that the vm has been join the zerotier network.")
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertNotEqual(len(result), 0)

    @unittest.skip("we don't know what's the configuration of network we should use")
    def test007_create_gateway_with_passthrough_and_zerotier_vm(self):
        """SAL-GW-017
        *Test case for deploying gateways with passthrough and zerotier networks . *
        Test Scenario:

        #. Create new zerotier network.
        #. Create gateway with public passthrough network , should succeed.
        #. Add zerotier network as private network by pass zerotier client, should succeed.
        #. Adding a new vm t to gateway private network , should succeed.
        #. Check that the vm has been join the zerotier .
        """
        self.log("[*] Create new zerotier network.")
        zt_network_name = self.random_string()
        zt_network = self.zt_client.network_create(public=False, name=zt_network_name, auto_assign=True, subnet='10.142.13.0/24')
        self.host_join_zt(zt_network)
        zt_node_ip = self.zos_node_join_zt(zt_network.id)

        self.log("[*] Create gateway with public passthrough public network, should succeed.")
        self.gateway.generate_gw_sal()
        public_network_name = self.random_string()
        public_net = self.gateway.add_network(name=public_network_name, type_="passthrough", networkid='eth1')        
        public_net.ip.cidr = "%s/24"%zt_node_ip
        public_net.ip.gateway = zt_node_ip.replace(zt_node_ip.rsplit(".")[3], '1')

        self.log("Add zerotier network as private network, should succeed.")
        zt_network = self.gateway.add_zerotier(self.zt_network)
        self.gateway.install()

        self.log("Adding a new vm t to gateway private network , should succeed.")
        self.vm.install()
        self.vms.append(self.vm.info()['uuid'])
        zt_network.hosts.add(self.vm.vm_sal)
        self.vm.install()
        self.gateway.install()

        self.log("Check that the vm has been join the zerotier network.")
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertNotEqual(len(result), 0)

  
class GWActions(BaseTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.log(" Create gateway with default and zerotier network, should succeeed.")
        self.gateway = self.gw(node=self.node_sal)
        self.gateway.data = self.set_gw_default_values()
        self.gateway.generate_gw_sal()
        self.public_network_name = 'n'+self.random_string()
        self.public_network = self.gateway.add_network(name=self.public_network_name, type_="default")        
        self.public_network.public = True
        self.private_network = self.gateway.add_zerotier(self.zt_network)

        self.log("Create vm[vm1] with same zerotier network, should succceed.")
        self.vm_data = self.set_vm_default_values(os_type="ubuntu")
        self.vm = self.vm(node=self.node_sal, data=self.vm_data)
        self.vm.generate_vm_sal()
        self.vm.add_zerotier_nics(self.zt_network)
        self.vm.install()
        self.ztIdentity = self.vm.data["ztIdentity"]
        self.vm_zt_ip = self.get_zerotier_ip(self.ztIdentity)
        self.vms.append(self.vm.info()['uuid'])

    def tearDown(self):
        self.gateway.destroy()
        self.log("destroy created vms.")
        for uuid in self.vms:
            self.node_sal.client.kvm.destroy(uuid)
        self.vms.clear()

    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/132")
    def test008_create_gateway_portforwards(self):
        """SAL-GW-018
        * Test case for create gateway portforward.
        Test Scenario:

        #. Create gateway with default network as public and zerotier as private network , should succeeed .
        #. Create vm[vm1] with same zerotier network and deploy it , should succceed.
        #. Create server on the vm at specific port. 
        #. Set a portforward to gw from from public network to vm server port, should succeed.
        #. Deploy the gateway[gw], should succeed.
        #. Try to request a service on [vm1] server and make sure that u can reach this vm.
        """
        server_port = random.randint(3000, 4000)
        self.log("create server on the vm at port {}.".format(server_port))
        cmd = 'python3 -m http.server {} &> /tmp/server.log &'.format(server_port)
        self.ssh_vm_execute_command(vm_ip=self.vm_zt_ip, cmd=cmd)
        time.sleep(10)

        self.log("Set a portforward to gw from from public network to vm server port, should succeed.")
        public_port = random.randint(4000, 5000)
        self.gateway.add_port_forward('httpforward', (self.public_network_name, public_port), (self.vm_zt_ip, server_port))

        self.log("#. Deploy the gateway[gw], should succeed.")
        self.gateway.install()
        self.vm.install()

        self.log("Get the content of authorized_key file from the vm using the server created and portforward.")
        response = requests.get('http://{}:{}/.ssh/authorized_keys'.format(self.node_ip, public_port))
        content = response.content.decode('utf-8')

        self.log("Make sure that ssh key is in the authorized_key")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, self.ssh_key)

    def test09_add_multiple_portforward(self):
        """SAL-GW-019
        * Test case for create gateway with multiple portforward.
        Test Scenario:

        #. Create gateway with default and zerotier network, should succeeed .
        #. Create vm[vm1] with same zerotier network, should succceed.
        #. Set a specific  portforward [pf1] to gw from from public network to vm , should succeed.
        #. Try to set another portforward [pf2] with same name as pf1 and different ports , should fail.
        #. Try to set another portforward [pf3] with different name and different ports , should succeed.
        #. Deploy the gateway and check that both[pf1] and [pf2] exist.
        """

        self.log("Set a portforward to gw from from public network to vm server port, should succeed.")
        pf1_name = self.random_string()
        source_port1 = random.randint(1000, 2000)
        destination_port1 = random.randint(2000, 3000)
        self.gateway.add_port_forward(pf1_name, (self.public_network_name, source_port1), (self.vm_zt_ip, destination_port1))
    
        self.log("Try to set another portforward [pf2] with same name as pf1 and different ports , should fail.")
        source_port2 = random.randint(3000, 4000)
        destination_port2 = random.randint(4000, 5000)        
        with self.assertRaises(ValueError) as e:
            self.gateway.add_port_forward(pf1_name, (self.public_network_name, source_port2), (self.vm_zt_ip, destination_port2))
        self.assertIn("name %s already exists"%(pf1_name), e.exception.args[0])

        self.log("try to set another portforward [pf3] with different name and different ports , should succeed.")
        source_port3 = random.randint(5000, 6000)
        destination_port3 = random.randint(6000, 7000)        
        pf3_name = self.random_string()
        self.gateway.add_port_forward(pf3_name, (self.public_network_name, source_port3), (self.vm_zt_ip, destination_port3))

        self.log("Deploy the gateway and check that both[pf1] and [pf2] exist.")
        self.gateway.install()
        gw_container = self.get_gateway_container(self.gateway.data["name"])
        gw_ports = list(gw_container['container']['arguments']['port'].values())
        self.assertIn(source_port3, gw_ports)
        self.assertIn(source_port1, gw_ports)
        
    @unittest.skip("https://github.com/threefoldtech/jumpscale_lib/issues/132")
    def test001_remove_portforward(self):
        """SAL-GW-020
        * Test case for remove portforward from gateway .
        Test Scenario:

        #. Create gateway with default and zerotier network, should succeeed.
        #. Create vm[vm1] with same zerotier network, should succceed.
        #. Set a specific  portforward [pf1] to gw from from public network to vm , should succeed.
        #. Deploy the gateway and check that [pf1] is  exist.
        #. Remove [pf1]from the gateway, 
        #. Check that [pf1] has been deleted successfully.
        """

        self.log("Set a portforward to gw from from public network to vm server port, should succeed.")
        pf_name = self.random_string()
        source_port = random.randint(3000, 4000)
        destination_port = random.randint(3000, 4000)
        self.gateway.add_port_forward(pf_name, (self.public_network_name, source_port), (self.vm_zt_ip, destination_port))

        self.log("Deploy the gateway and check that both[pf1] and [pf2] exist.")
        self.gateway.install()
        gw_container = self.get_gateway_container(self.gateway_data["name"])
        gw_ports = list(gw_container['container']['arguments']['port'].values())
        self.assertIn(source_port, gw_ports)

        self.log(" Remove [pf1] from the gateway, ")
        self.gateway.remove_port_forward(pf_name)
        self.gateway.install()

        self.log("Check that [pf1] has been deleted successfully.")
        gw_container = self.get_gateway_container(self.gateway_data["name"])
        gw_ports = list(gw_container['container']['arguments']['port'].values())
        self.assertNotIn(source_port, gw_ports)

