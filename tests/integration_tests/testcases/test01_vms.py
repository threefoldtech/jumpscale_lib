from framework.base.vms import VM
from testcases.base_test import BaseTest


class VMTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        pass

    def test001_create_vm(self):
        """ SAL-001 Install zerotier vm.

        **Test Scenario:**
 
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Check that vm added to zerotier network and can access it using it, should succeed.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        self.vm.data = self.set_vm_default_values(os_type="ubuntu")
        vm1 = self.vm._vm_sal
        self.assertTrue(vm1)
        
        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(vm1)
        self.vm.install(vm1)

        self.log("Check that vm added to zerotier network and can access it using it, should succeed.")
        ztIdentity = self.vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertNotEqual(len(result), 0)

    def test002_create_vm_with_type_default(self):
        """ SAL-002 create vm with type default.

        **Test Scenario:**
 
        #. Create vm [VM1] with type default, should succeed.
        #. Check that vm can reach internet, should suucceed.

        """
        pass