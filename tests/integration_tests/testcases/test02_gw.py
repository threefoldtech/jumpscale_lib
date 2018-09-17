from testcases.base_test import BaseTest
from nose_parameterized import parameterized
from termcolor import colored
import unittest
import time

class GWTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.gateway_data = self.set_gw_default_values()
        self.gateway = self.gw(node=self.node_sal, data=self.gateway_data)
        self.vm_data = self.set_vm_default_values(os_type="ubuntu")
        self.vm = self.vm(node=self.node_sal, data=self.vm_data)

    def tearDown(self):
        self.gateway.destroy()

    def test001_deploy_getway_without_public_network(self):
        """SAL-GW-000
        *Test case for deploying gateway without default public network .
        Test Scenario:

        #. Create gateways[GW1] without network interface, should succeed.
        #. Deploy [GW1], should fail as there is no public network.
        """
        self.log(" Deploy [GW1], should fail .")
        try:
            self.gateway.install()
        except RuntimeError as e:
            self.assertIn("Need exactly one public network", e.args[0])

    def test002_deploy_getway_with_public_network(self):
        """SAL-GW-000
        *Test case for deploying gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1], should succeed.
        #. Attach default network to [GW1] and don't set network public to True .
        #. Deploy [GW1], should fail ,need at least one public network.
        #. Set network public to True.
        #. Deploy [GW1], should succeed.
        """
        self.log("Create gateways[GW1], should succeed.")
        created_gateway = self.gateway._gateway_sal

        self.log("Attach default network to [GW1] and don't set network public to True .")
        network = created_gateway.networks.add(name="public", type_="default")

        self.log("Deploy [GW1], should fail ,need at least one public network.")
        try:
            self.gateway.install()
        except RuntimeError as e:
            self.assertIn("Need exactly one public network", e.args[0])

        self.log("Set network public to True.")
        network.public = True

        self.log("Deploy [GW1], should succeed.")
        self.gateway.install()

    def test003_add_network_name_exist(self):
        """SAL-GW-000
        *Test case for deploying gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1], should succeed.
        #. Add network [N1] to [GW1], should succeed.
        #. Add network [N2] with same type and same name as [N1] to [GW1],should fail .
        #. Add network [N3] with different type and same name as [N1] to [GW1],should fail .
        """

        created_gateway = self.gateway._gateway_sal

        self.log(" Add network [N1] to [GW1], should succeed.")
        network_name = self.random_string()
        network = created_gateway.networks.add(name=network_name, type_="default")
        self.gateway.install(created_gateway)

        self.log("Add network [N2] with same type and same name as [N1] to [GW1],should fail .")
        try:
            created_gateway.networks.add(name=network_name, type_="default")
        except ValueError as e:
            self.assertIn(" Element with name %s already exists"%network_name, e.args[0])

        self.log("Add network [N2] with different type and same name as [N1] to [GW1],should fail .")
        try:
            created_gateway.networks.add(name=network_name, type_="zerotier", networkid=self.zt_network.id)
        except ValueError as e:
            self.assertIn(" Element with name %s already exists"%network_name, e.args[0])

    def test04_remove_network(self):
        """SAL-GW-000
        *Test case for deploying gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1], should succeed.
        #. Add network [N1] to [GW1], should succeed.
        #. Deploy [GW1], should succeed.
        #. Remove N1, should succeed. 
        #. Check that network has been removed.
        """

        created_gateway = self.gateway._gateway_sal
        self.log("Add network [N1] to [GW1], should succeed.")
        network_name = self.random_string()
        created_network = created_gateway.networks.add(name=network_name, type_="default")        

        self.log("Deploy [GW1], should succeed.")
        self.gateway.install()
        
        self.log("remove N1, should succeed.")
        created_gateway.networks.remove(created_network)
        created_gateway.deploy()

        self.log("Check that network has been removed.")
        self.assertFalse(created_gateway.networks.list())

    def test05_deploy_getways_with_public_network(self):
        """SAL-GW-000
        *Test case for deploying more than one gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1],[GW2], should succeed.
        #. Attach default network to [GW1] and [GW2] ,then set network public to True .
        #. Deploy [GW1], should succeed
        #. Deploy [GW2], should fail as we can create only one gateway with type defaulgt public network.
        """
        self.log("Create gateways[GW1],[GW2], should succeed.")
        gw2_data = self.set_gw_default_values()

        gateway2 = self.gw(node=self.node_sal, data=gw2_data)
        gw1 = self.gateway._gateway_sal
        gw2 = gateway2._gateway_sal

        self.log("Attach default network to [GW1] and [GW2] ,then set network public to True.")
        network1 = gw1.networks.add(name="public", type_="default")
        network1.public = True
        network2 = gw2.networks.add(name="public", type_="default")
        network2.public = True

        self.log(" Deploy [GW1], should succeed")
        self.gateway.install(gw1)

        self.log("Deploy [GW2], should fail as we can create only one gateway with type defaulgt public network.")
        try:
            gateway2.install(gw2)

        except RuntimeError as e:
            self.assertIn("port already in use", e.args[0])

    def test06_create_gateway_with_public_and_zerotier_vm(self):
        """SAL-GW-000
        *Test case for deploying gateways with public and zerotier networks. *
        Test Scenario:

        #. Create gateway with public default network, should succeed.
        #. Add zerotier network as private network, should succeed.
        #. Adding a new vm t to gateway private network , should succeed.
        #. Check that the vm has been join the zerotier network.
        """
        created_gateway = self.gateway._gateway_sal
        self.log("Create gateway with public default network, should succeed.")
        network_name = self.random_string()
        created_network = created_gateway.networks.add(name=network_name, type_="default")        

        self.log("Add zerotier network as private network, should succeed.")
        
        zt_network = created_gateway.networks.add_zerotier(self.zt_network)

        self.log("Adding a new vm t to gateway private network , should succeed.")
        self.vm.deploy()
        zt_network.hosts.add(self.vm)
        self.gateway.deploy()
        self.vm.deploy()

        self.log("Check that the vm has been join the zerotier network.")
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertNotEqual(len(result), 0)

    @unittest.skip("we don't know what's the configuration of network we should use")
    def test007_create_gateway_with_passthrough_and_zerotier_vm(self):
        """SAL-GW-000
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
        created_gateway = self.gateway._gateway_sal
        public_network_name = self.random_string()
        public_net = created_gateway.networks.add(name=public_network_name, type_="passthrough", networkid='eth1')        
        public_net.ip.cidr = "%s/24"%zt_node_ip
        public_net.ip.gateway = zt_node_ip.replace(zt_node_ip.rsplit(".")[3], '1')

        self.log("Add zerotier network as private network, should succeed.")
        zt_network = created_gateway.networks.add_zerotier(self.zt_network)
        created_gateway.deploy()

        self.log("Adding a new vm t to gateway private network , should succeed.")
        self.vm.deploy()
        zt_network.hosts.add(self.vm)
        self.vm.deploy()
        created_gateway.deploy()

        self.log("Check that the vm has been join the zerotier network.")
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertNotEqual(len(result), 0)



    # def test008_create_gateway_portforwards():
    #     """SAL-GW-000
    #     * Test case for create gateway portforward.
    #     Test Scenario:

    #     #. Create bridge(B0) , should succeed. 
    #     #. Create gateway with default network as public and zerotier as private network , should succeeed .
    #     #. Set a portforward from from public network to to private, should succeed.
    #     #. Create one container as a destination host
    #     #. Adding a vm[vm1] host to gateway private network , should succeed.
    #     #. Try to request a service on vm1 and make sure that u can reach this vm.
    #     """
    #     pass 

    # def test09_create_gateway_httpproxy():
    #     """SAL-GW-000
    #     *Test case for deploying gateways with httpproxy. *
    #     Test Scenario:

    #     #. Create gateway with public passthrough and private zerotier network , should succeed.
    #     #. Create vm[vm1] and run simple server inside it on specific port.
    #     #. Adding a new vm t to zerotier gateway private network , should succeed.
    #     #. Create domain with node public ip.
    #     #. Add a http proxy with created domain, and vm zerotier ip with server port.
    #     #. Check that you can get https server.
    #     """
    #     pass

    # def test10_add_portforward_before_start(self):
    #     pass
    # def test11_add_portforward_name_exists(self):
    #     pass
    # def test12_add_portforward_combination_exists_different_protocols(self):
    #     pass
    # def test13_remove_portforward(self):
    #     pass
    # def test14_remove_portforward_before_start(self):
    #     pass
    # def test15_add_http_proxy_before_start(self):
    #     pass
    # def test16_add_http_proxy_name_exists(self):
    #     pass
    # def test17_add_http_proxy_host_exists(self):
    #     pass
    # def test18_remove_http_proxy(self):
    #     pass
    # def test19_add_dhcp_host(self):
    #     pass
    # def test20_remove_dhcp_host(self):
    #     pass

    # def test21_add_network(self):
    #     pass

    # def test22_stop(self):
    #     pass

    # def test23_gateway_cloudinit(self):
    #     pass

