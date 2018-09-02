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

    def test002_create_vm_with_different_os_types(self):
        """SAL-VM-002
        * Test case for creating a vm with ubuntue and zero-os operating system .
        Test Scenario:

        #. Create a vm [vm1] with latest version of ubuntue, should succeed.
        #. Create a vm[vm2] with speceific version of ubuntue, should succeed.
        #. Check that vm1 and vm2 created with right ubuntue versions .
        #. Create vm[vm3] with zero-os , should succeed.
        #. Create vm [vm4] with zero-os developement branch, should succeed.
        #. Chec that [vm3] and [vm4] created with right zero-os version and works well.
        """
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test003_create_vm_with_type_default(self, os_type):
        """ SAL-003 create vm with type default.

        **Test Scenario:**
 
        #. Create vm [VM1] with type default, should succeed.
        #. Check that vm can reach internet, should suucceed.

        """
        pass

    def test004_destroy_vm(self, os_type):
        """ SAL-004 destroy the vm .

        **Test Scenario:**
 
        #. Create vm [VM1], should succeed.
        #. Destroy vm [VM1], should succeed.
        #. Check that vm [vm1] has been removed successfully.

        """
        self.log(" Create vm [VM1], should succeed.")
        self.vm.data = self.set_vm_default_values(os_type="ubuntu")
        self.vm.install()
        self.assertTrue(self.vm._vm_sal.is_running())

        self.log("Destroy vm [VM1], should succeed.")
        self.vm.uninstall()
        self.assertFalse(self.vm._vm_sal.is_running())


    @parameterized.expand(["zero-os", "ubuntu"])
    def test005_add_and_delete_disk_from_vm(self, os_type):
        """ SAL-005 add and delete disk to the vm .

        **Test Scenario:**
 
        #. Create vm [VM1], should succeed.
        #. Attach disk[D1] to vm1, should succeed.
        #. Check that disk [D1]added successfully to vm1.
        #. Remove the disk[D1] from the disk ,should succeed.
        #. Check that disk removed successfully.

        """
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test006_add_and_drop_vm_ports(self, os_type):
        """ SAL-006 add and drop ports to the vm .

        **Test Scenario:**
 
        #. Create vm [VM1], should succeed.
        #. Add port to [p1] to [VM1], should succeed.
        #. Start server on P1, should succeed.
        #. Check that u can access that server through [P1].
        #. Drop [P1] ,should succeed.
        #. Check that you can't access the server anymore.

        """
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test007_add_and_delete_zerotier_network_to_vm(self):
        """ SAL-007 add and delete zerotier network to vm  .

        **Test Scenario:**
 
        #. Create vm [VM1] and deploy it , should succeed.
        #. Add Zerotier network to [VM1], should fail as vm is running.
        #. Create vm [Vm2] ,should succeed.
        #. Add Zerotier network to [VM2] before deploy it , should succeed.
        #. Check that vm [VM2] join zerotier successfully after deploy it.
        """
        pass      


class VMActionsBase(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.vm.data = self.set_vm_default_values(os_type="ubuntu")
        self.ubuntu_vm = self.vm._vm_sal   

        self.vm.data = self.set_vm_default_values(os_type="zero-os")
        self.zero_os_vm = self.vm._vm_sal                
    
    def tearDown(self):
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test001_enable_and_disable_vm_vnc(self):
        """ SAL-008 enable and disable the vnc port on the vm.

        **Test Scenario:**
 
        #. Create vm [VM1] with default values, should succeed.
        #. Try to connect to vnc port of vm1, should fail.
        #. Enable vnc port of [vm1] and connecto to it , should succeed.
        #. Disable vnc port of [vm1] , should succeed.
        #. Try to connect to vnc port again , should fail.

        """
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test002_pause_and_resume_vm(self):
        """ SAL-008 pause and resume the vm with type default.

        **Test Scenario:**
 
        #. Create a vm[vm1]  on node, should succeed.
        #. Pause [vm1], should succeed.
        #. Check that [vm1] has been paused successfully.
        #. Resume [vm1], should succeed.
        #. Check that [vm1] is runninng and can access it again.

        """
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test003_reset_and_reboot_vm(self):
        """ SAL-009 reset and reboot the vm.

        **Test Scenario:**
 
        #. Create a vm[vm1]  on node, should succeed.
        #. Enable vnc_port for [vm1], should succeed.
        #. Reset or reboot the vm, should suceeed.
        #. Check that [vm] has been rebooted/reset successfully.
        """
        pass

    @parameterized.expand(["zero-os", "ubuntu"])
    def test004_shutdown_and_start_vm(self):
        """ SAL-010
        *Test case for testing shutdown and start vm*

        **Test Scenario:**

        #. Create a vm[vm1], should succeed.
        #. Shutdown [vm1], should succeed.
        #. Check that [vm1] has been forced shutdown successfully.
        #. Start [vm1], should succeed.
        #. Check that [vm1] is running again.

        """