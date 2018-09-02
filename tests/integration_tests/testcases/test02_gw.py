from framework.base.vms import VM
from testcases.base_test import BaseTest
from nose_parameterized import parameterized


class VMTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        pass

    def test001_deploy_getways_with_public_network(self):
        """SAL-GW-000
        *Test case for deploying more than one gateway with default public network .
        Test Scenario:

        #. Create gateways[GW1],[GW2], should succeed.
        #. Attach default network to [GW1] and set network public to True .
        #. Deploy [GW1], should succeed
        #. Attach default network to [GW2] and set network public to True .
        #. Deploy [GW2], should fail as we can create only one gateway with type defaulgt public network.
        """

    def test002_create_gateway_with_passthrough_and_zerotier_vm():
        """SAL-GW-000
        *Test case for deploying gateways with passthrough and zerotier networks . *
        Test Scenario:

        #. Create new zerotier network.
        #. Create gateway with public passthrough network , should succeed.
        #. Add zerotier network as private network by pass zerotier client, should succeed.
        #. Adding a new vm t to gateway private network , should succeed.
        #. Check that the vm has been join the zerotier network.
        """
        pass

    def test003_create_gateway_portforwards():
        """SAL-GW-000
        * Test case for create gateway portforward.
        Test Scenario:

        #. Create bridge(B0) , should succeed. 
        #. Create gateway with default network as public and zerotier as private network , should succeeed .
        #. Set a portforward from from public network to to private, should succeed.
        #. Create one container as a destination host
        #. Adding a vm[vm1] host to gateway private network , should succeed.
        #. Try to request a service on vm1 and make sure that u can reach this vm.
        """

    def test_add_portforward_before_start(self):
        pass
    def test_add_portforward_name_exists(self):
        pass
    def test_add_portforward_combination_exists_different_protocols(self):
        pass
    def test_remove_portforward(self):
        pass
    def test_remove_portforward_before_start(self):
        pass
    def test_add_http_proxy_before_start(self):
        pass
    def test_add_http_proxy_name_exists(self):
        pass
    def test_add_http_proxy_host_exists(self):
        pass
    def test_remove_http_proxy(self):
        pass
    def test_add_dhcp_host(self):
        pass
    def test_remove_dhcp_host(self):
        pass
    def test_start(self):
        pass
    def test_start_not_installed(self):
        pass
    def test_add_network(self):
        pass
    def test_add_network_name_exist(self):
        pass
    def test_remove_network(self):
        pass
    def test_remove_network(self):
        pass
    def test_uninstall(self):
        pass
    def test_stop(self):
        pass
    def test_gateway_cloudinit(self):
        pass

    def test04_create_gateway_httpproxy():
        """SAL-GW-000
        *Test case for deploying gateways with httpproxy. *
        Test Scenario:

        #. Create gateway with public passthrough and private zerotier network , should succeed.
        #. Create vm[vm1] and run simple server inside it on specific port.
        #. Adding a new vm t to zerotier gateway private network , should succeed.
        #. Create domain with node public ip.
        #. Add a http proxy with created domain, and vm zerotier ip with server port.
        #. Check that you can get https server.
