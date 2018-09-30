from framework.base.vms import VM
from testcases.base_test import BaseTest
from nose_parameterized import parameterized
import time
import unittest
import requests
import random

class VMTestCases(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        self.log("destroy created vms.")
        for uuid in self.vms:
            self.node_sal.client.kvm.destroy(uuid)
        self.vms.clear()

    @parameterized.expand(["zero-os", "ubuntu"])
    def test001_create_vm(self, os_type):
        """ SAL-001 Install zerotier vm.

        **Test Scenario:**
 
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Check that vm added to zerotier network and can access it using it, should succeed.

        """
        if os_type == 'zero-os':
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/102')

        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type=os_type)
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)
       
        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(created_vm)
        vm.install(created_vm)
        self.vms.append(created_vm.uuid)

        self.log("Check that vm added to zerotier network and can access it using it, should succeed.")
        ztIdentity = vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertEqual(result, '/root')

    @parameterized.expand(["zero-os", "ubuntu"])
    def test002_create_vm_with_different_os_types(self, os_type):
        """SAL-002 
        * Test case for creating a vm with ubuntu and zero-os operating system .
        Test Scenario:

        #. Create a vm [vm1] with one of (ubuntu/zero-os) version, should succeed.
        #. Check that vm1 created with right (ubuntu/zero-os) versions.

        """
        if os_type == 'ubuntu':
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/111')
            version_release = random.choice(["16.04", "18.04"])
            cmd = 'lsb_release -r'
        else:
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/102')
            version_release = random.choice(["master", "development"])
            cmd = 'core0'

        self.log(" Create a vm [vm1] with {} version of {}, should succeed.".format(version_release, os_type))
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type=os_type, os_version=version_release)
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)

        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(created_vm)
        vm.install(created_vm)
        self.vms.append(created_vm.uuid)
        
        self.log("Check that vm2 added to zerotier network and can access it using it, should succeed.")
        ztIdentity = vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd=cmd)

        self.log("Check that vm1 and vm2 created with right {} versions.".format(os_type))
        if os_type == 'ubuntu':
            result = result.replace('\t', '')
            release = result[result.find(':') + 1 :]
        else:
            release = result[result.find(':') + 2 : result.find('@') - 1]
        self.assertEqual(release, version_release)

    def test003_create_vm_with_type_default(self):
        """ SAL-003 create vm with type default.

        **Test Scenario:**
 
        #. Create vm [VM1] with type default nics, should succeed.
        #. Add a port forward to port 22.
        #. Check that vm can reach internet, should succeed.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")

        self.log("Update default data by adding type default nics")
        network_name = self.random_string()
        nics = {'nics': [{'name': network_name, 'type': 'default'}]}  
        vm.data = self.update_default_data(vm.data, nics)

        created_vm = vm._vm_sal
        self.assertTrue(created_vm)

        self.log("Add a port forward to port 22.")
        port_name = self.random_string()  
        host_port_ssh = random.randint(7000, 8000)       
        created_vm.ports.add(name=port_name, source=host_port_ssh, target=22)
        
        vm.install(created_vm)
        self.vms.append(created_vm.uuid)
        
        self.log("Check that vm can reach internet, should succeed.")
        result = self.ssh_vm_execute_command(vm_ip=self.node_ip, port=host_port_ssh, cmd='ping -w5 8.8.8.8')
        self.assertIn('0% packet loss', result) 

    @parameterized.expand(["zero-os", "ubuntu"])
    def test004_destroy_vm(self, os_type):
        """ SAL-004 destroy the vm .

        **Test Scenario:**
 
        #. Create vm [VM1], should succeed.
        #. Destroy vm [VM1], should succeed.
        #. Check that vm [vm1] has been removed successfully.

        """
        self.log(" Create vm [VM1], should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type=os_type)
        vm.install()
        self.assertTrue(vm._vm_sal.is_running())

        self.log("Destroy vm [VM1], should succeed.")
        vm.uninstall()
        self.assertFalse(vm._vm_sal.is_running())

    @parameterized.expand(["zero-os", "ubuntu"])
    def test005_add_and_delete_disk_from_vm(self, os_type):
        """ SAL-005 add and delete disk to the vm .

        **Test Scenario:**
 
        #. Create vm [VM1], should succeed.
        #. Attach disk[D1] to vm1, should succeed.
        #. Check that disk [D1] added successfully to vm1.
        #. Try to attach disk[D1] again to vm1, should failed.
        #. Remove the disk[D1] from the vm ,should succeed.
        #. Check that disk removed successfully.

        """
        if os_type == 'zero-os':
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/102')

        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type=os_type)
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)
        
        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(created_vm)
        vm.install(created_vm)
        self.vms.append(created_vm.uuid)

        self.log("Check that vm added to zerotier network and can access it using it, should succeed.")
        ztIdentity = vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertEqual(result, '/root')

        self.log("Check that vm don't attach any disk.")
        self.assertFalse(created_vm.info['params']['media'])

        self.log("Get disk name and url(path).")
        host_disk = self.node_sal.client.disk.list()[0]['name']
        disk_url = '/dev/{}'.format(host_disk)

        self.log("Attach disk[D1] to vm1, should succeed.")
        disk_name1 = self.random_string()
        created_vm.disks.add(name_or_disk=disk_name1, url=disk_url)
        created_vm.update_disks()

        self.log("Check that disk [D1] added successfully to vm1.")
        self.assertEqual(created_vm.info['params']['media'][0]['url'], disk_url)

        self.log("Try to attach disk[D1] again to vm1, should failed.")
        disk_name2 = self.random_string()
        created_vm.disks.add(name_or_disk=disk_name2, url=disk_url)
        
        with self.assertRaises(RuntimeError) as e:
            created_vm.update_disks()
        self.assertIn('The disk you tried is already attached to the vm', e.exception.args[0])

        self.log('Remove the disk[D1] from the vm ,should succeed.')
        created_vm.disks.remove(disk_name1)
        created_vm.disks.remove(disk_name2)
        created_vm.update_disks()

        self.log('Check that disk removed successfully.')
        self.assertFalse(created_vm.info['params']['media'])

    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/93')
    def test006_add_remove_port_to_vm(self):
        """ SAL-006 add server on vm port .

        **Test Scenario:**
 
        #. Create vm [VM1], should succeed.
        #. Add port to [p1] to [VM1], should succeed.
        #. Start server on P1, should succeed.
        #. Check that you can access that server through [P1].
        #. Drop port [p1]
        #. Check that you can't access the server anymore, should succeed.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")

        self.log("Update default data by adding type default nics")
        network_name = self.random_string()
        nics = {'nics': [{'name': network_name, 'type': 'default'}]}  
        vm.data = self.update_default_data(vm.data, nics)
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)

        self.log("Add 2 port forward for ssh and server.")
        port_name1 = self.random_string()
        host_port_ssh = random.randint(1000, 2000)        
        created_vm.ports.add(name=port_name1, source=host_port_ssh, target=22)
        
        port_name2 = self.random_string()   
        host_port = random.randint(3000, 4000)
        guest_port = random.randint(5000, 6000)
        created_vm.ports.add(name=port_name2, source=host_port, target=guest_port)
        vm.install(created_vm)
        self.vms.append(created_vm.uuid)
        
        self.log("create server on the vm at port {}.".format(guest_port))
        cmd = 'python3 -m http.server {} &> /tmp/server.log &'.format(guest_port)
        self.ssh_vm_execute_command(vm_ip=self.node_ip, port=host_port_ssh, cmd=cmd)
        time.sleep(10)
        
        self.log("Get the content of authorized_key file from the vm using the server created ")
        response1 = requests.get('http://{}:{}/.ssh/authorized_keys'.format(self.node_ip, host_port))
        content1 = response1.content.decode('utf-8')

        self.log("Make sure that ssh key is in the authorized_key")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(content1, self.ssh_key)
      
        self.log("Drop port [p1]")
        created_vm.ports.remove(port_name2)
        vm.install()

        self.log("Check that you can't access the server anymore, should succeed")
        with self.assertRaises(ConnectionError):
            requests.get('http://{}:{}/.ssh/authorized_keys'.format(self.node_ip, host_port))

    @parameterized.expand(["zero-os", "ubuntu"])
    def test007_add_and_delete_zerotier_network_to_vm(self, os_type):
        """ SAL-007 add and delete zerotier network to vm  .

        **Test Scenario:**
 
        #. Create vm [VM1] and deploy it , should succeed.
        #. Add Zerotier network to [VM1], should fail as vm is running.
        #. Create vm [VM2] ,should succeed.
        #. Add Zerotier network to [VM2] before deploy it , should succeed.
        #. Check that vm [VM2] join zerotier successfully after deploy it.
        """
        if os_type == 'zero-os':
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/102')

        self.log("create vm [VM1] and deploy it , should succeed.")
        vm1 = self.vm(node=self.node_sal)
        vm1.data = self.set_vm_default_values(os_type=os_type)
        created_vm1 = vm1._vm_sal
        self.assertTrue(created_vm1)   
        vm1.install(created_vm1)
        self.vms.append(created_vm1.uuid)

        self.log("Add Zerotier network to [VM1], should fail as vm is running.")
        with self.assertRaises(RuntimeError) as e:
            self.add_zerotier_network_to_vm(created_vm1)
        self.assertIn('Zerotier can not be added when the VM is running', e.exception.args[0])

        self.log("Create vm [VM2] ,should succeed.")
        vm2 = self.vm(node=self.node_sal)
        vm2.data = self.set_vm_default_values(os_type=os_type)
        created_vm2 = vm2._vm_sal
        self.assertTrue(created_vm2)

        self.log("Add Zerotier network to [VM2] before deploy it , should succeed.")
        self.add_zerotier_network_to_vm(created_vm2)
        vm2.install(created_vm2)
        self.vms.append(created_vm2.uuid)

        self.log("Check that vm [VM2] join zerotier successfully after deploy it.")
        ztIdentity = vm2.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertEqual(result, '/root')

    def test008_add_port_without_type_default_nics_to_vm(self):
        """ SAL-020 create vm without type default and add port.

        **Test Scenario:**
 
        #. Create vm [vm1] with default values, should succeed.
        #. Add a port forward to port 22, should fail.
        #. Add type default to [vm1].
        #. Add a port forward to port 22 again, should succeed.
        #. Check that you can access [vm1], should succeed.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)

        self.log("Add a port forward to port 22, should fail.")
        port_name = self.random_string()
        host_port = random.randint(3000, 4000)

        with self.assertRaises(ValueError) as e:
            created_vm.ports.add(port_name, source=host_port, target=22)
        self.assertIn('Can not add ports when no default nic is added', e.exception.args[0])

        self.log("Add type default to [vm1].")
        network_name = self.random_string()
        created_vm.nics.add(type_='default', name=network_name)

        self.log("Add a port forward to port 22.")
        created_vm.ports.add(port_name, source=host_port, target=22)
    
        vm.install(created_vm)
        self.vms.append(created_vm.uuid)

        self.log("Check that you can access [vm1], should succeed.")
        result = self.ssh_vm_execute_command(vm_ip=self.node_ip, port=host_port, cmd='pwd')
        self.assertEqual(result, '/root') 

    @parameterized.expand(["name", "vcpus", "memory", "flist"])
    def test009_change_vm_params(self, param):
        """ SAL-021 change vm parameters.

        **Test Scenario:**
 
        #. Create vm [VM1] with default values, should succeed.
        #. Try to change vm parameters while it is running, should fail.
        #. Force shutdown the vm.
        #. Change vm paramters, should succeed.
        #. Start the vm again.
        #. Check that vm parameters are changed.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)
        vm.install(created_vm)

        if param == "name":
            new_param_val = self.random_string()
            flag = param
        elif param == "vcpus":
            new_param_val = random.randint(1, 3)
            flag = "cpu"
        elif param == "memory":
            new_param_val = random.randint(1, 3) * 1024
            flag = param
        else:
            new_param_val = 'https://hub.grid.tf/tf-bootable/ubuntu:16.04.flist'
            flag = param

        self.log("Try to change vm {} while it is running, should fail.".format(param))
        with self.assertRaises(RuntimeError) as e:
            setattr(created_vm, param, new_param_val)
        self.assertIn('Can not change {} of running vm'.format(flag), e.exception.args[0])

        self.log("Change vm parameters, should succeed.")
        created_vm.destroy()
        setattr(created_vm, param, new_param_val)

        self.log("Start the vm again.")
        created_vm.start()
        self.vms.append(created_vm.uuid)

        self.log("Check that vm parameters are changed.")
        self.assertEqual(created_vm.info['params'][flag], new_param_val)

    def test010_ping_vms(self):
        """ SAL-022 check that vms with type default nics can reach each other

        **Test Scenario:**
 
        #. Create vm [VM1] with type default nics, should succeed.
        #. Add port forward to port 22.
        #. Create vm [VM2] with type default nics, should succeed.
        #. Create vm [VM3] without type default nics, should succeed.
        #. Try to ping VM2 from VM1, should succeed.
        #. Try to ping VM3 from VM1, should fail.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        vm1 = self.vm(node=self.node_sal)
        vm1.data = self.set_vm_default_values(os_type="ubuntu")

        self.log("Update default data by adding type default nics.")
        network_name = self.random_string()
        nics = {'nics': [{'name': network_name, 'type': 'default'}]}  
        self.update_default_data(vm1.data, nics)
        created_vm1 = vm1._vm_sal
        self.assertTrue(created_vm1)

        self.log("Add port forward to port 22.")
        port_name = self.random_string()
        host_port_ssh = random.randint(1000, 2000)        
        created_vm1.ports.add(name=port_name, source=host_port_ssh, target=22)
        vm1.install(created_vm1)
        self.vms.append(created_vm1.uuid)
        
        self.log("Create vm [VM2] with type default nics, should succeed.")
        vm2 = self.vm(node=self.node_sal)
        vm2.data = self.set_vm_default_values(os_type="ubuntu")

        self.log("Update default data by adding type default nics.")
        nics = {'nics': [{'name': network_name, 'type': 'default'}]}  
        vm2.data = self.update_default_data(vm2.data, nics)
        created_vm2 = vm2._vm_sal
        self.assertTrue(created_vm2)

        vm2.install(created_vm2)
        self.vms.append(created_vm2.uuid)

        self.log("Create vm [VM3] without type default nics, should succeed.")
        vm3 = self.vm(node=self.node_sal)
        vm3.data = self.set_vm_default_values(os_type="ubuntu")
        created_vm3 = vm3._vm_sal
        self.assertTrue(created_vm3)

        vm3.install(created_vm3)
        self.vms.append(created_vm3.uuid)

        self.log("Try to ping VM2 from VM1, should succeed.")
        cmd2 = 'ping -w5 "{}"'.format(created_vm2.info['default_ip'])
        result2 = self.ssh_vm_execute_command(vm_ip=self.node_ip, port=host_port_ssh, cmd=cmd2)
        self.assertIn('0% packet loss', result2)
        
        self.log("Try to ping VM3 from VM1, should fail.")
        cmd3 = 'ping -w5 "{}"'.format(created_vm3.info['default_ip'])
        response = self.execute_command(ip=self.node_ip, port=host_port_ssh, cmd=cmd3)
        self.assertTrue(response.returncode)       
        self.assertIn('100% packet loss', response.stdout)

    @unittest.skip('https://github.com/threefoldtech/jumpscale_lib/issues/97')
    def test011_ssh_with_different_ways(self):
        """ SAL-023 ssh with different ways

        **Test Scenario:**
 
        #. Create vm [VM1] with default values, should succeed.
        #. Add zerotier network to VM1, should succeed.
        #. Deploy the VM1 and check you can access it using ssh.should
        #. Add type default to VM1 and update nics, should succeed.
        #. Add port forward to port 22.
        #. Update the network and try to ssh using port forward, should succeed.

        """
        self.log("Create vm [VM1] with default values, should succeed.")
        vm = self.vm(node=self.node_sal)
        vm.data = self.set_vm_default_values(os_type="ubuntu")
        created_vm = vm._vm_sal
        self.assertTrue(created_vm)
       
        self.log("Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(created_vm)

        self.log("Deploy the vm1.")
        vm.install(created_vm)

        self.log("Check that vm added to zerotier network and can access it using it, should succeed.")
        ztIdentity = vm.data["ztIdentity"]
        vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        result1 = self.ssh_vm_execute_command(vm_ip=vm_zt_ip, cmd='pwd')
        self.assertEqual(result1, '/root')

        self.log("Add type default to vm1 and update nics, should succeed.")
        network_name = self.random_string()
        created_vm.nics.add(name=network_name, type_='default')

        self.log("Add port forward to port 22.")
        port_name = self.random_string()
        host_port_ssh = random.randint(8000, 9000)        
        created_vm.ports.add(name=port_name, source=host_port_ssh, target=22)
        
        self.log("Update the network and try to ssh using port forward, should succeed.")
        created_vm.update_nics()
        result2 = self.ssh_vm_execute_command(vm_ip=self.node_ip, port=host_port_ssh, cmd='pwd')
        self.assertEqual(result2, '/root') 

class VMActionsBase(BaseTest):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super().setUpClass()

    def setUp(self):
        super().setUp()
                        
    def tearDown(self):
        for uuid in self.vms:
            self.node_sal.client.kvm.destroy(uuid)
        self.vms.clear()

    def create_booted_vm(self, os_type):
        self.log("Create a vm[vm1]  on node, should succeed.")
        self.vm = self.vm(node=self.node_sal)
        self.vm.data = self.set_vm_default_values(os_type=os_type)
        self.created_vm = self.vm._vm_sal
        self.assertTrue(self.created_vm)
        
        self.log(" Add zerotier network to VM1, should succeed.")
        self.add_zerotier_network_to_vm(self.created_vm)
        self.vm.install(self.created_vm)
        self.vms.append(self.created_vm.uuid)

        self.log("Check that vm added to zerotier network and can access it using it, should succeed.")
        ztIdentity = self.vm.data["ztIdentity"]
        self.vm_zt_ip = self.get_machine_zerotier_ip(ztIdentity)
        # make sure that the machine is booted
        result = self.ssh_vm_execute_command(vm_ip=self.vm_zt_ip, cmd='pwd')
        self.assertEqual(result, '/root')

    @parameterized.expand(["zero-os", "ubuntu"])
    def test001_enable_and_disable_vm_vnc(self, os_type):
        """ SAL-008 enable and disable the vnc port on the vm.

        **Test Scenario:**
 
        #. Create vm [VM1] with default values, should succeed.
        #. Enable vnc port of [vm1] and connect to it , should succeed.
        #. Disable vnc port of [vm1] , should succeed.
        #. Try to connect to vnc port again , should fail.
        """
        self.log("Create a vm[vm1]  on node, should succeed.")
        self.vm = self.vm(node=self.node_sal)
        self.vm.data = self.set_vm_default_values(os_type=os_type)
        self.created_vm = self.vm._vm_sal
        self.assertTrue(self.created_vm)
        self.vm.install(self.created_vm)
        self.vms.append(self.created_vm.uuid)

        vnc_port = self.created_vm.info.get('vnc') - 5900

        self.log("Enable vnc port of [vm1] and connect to it , should succeed.")
        self.created_vm.enable_vnc()
        response2 = self.check_vnc_connection('{}:{}'.format(self.node_ip, vnc_port))
        self.assertFalse(response2.returncode)

        self.log("Disable vnc port of [vm1] , should succeed.")
        self.created_vm.disable_vnc()   

        self.log("Try to connect to vnc port again , should fail.")
        response3 = self.check_vnc_connection('{}:{}'.format(self.node_ip, vnc_port))
        self.assertTrue(response3.returncode)
        self.assertIn('timeout caused connection failure', response3.stderr.strip())

    @parameterized.expand(["zero-os", "ubuntu"])
    def test002_pause_and_resume_vm(self, os_type):
        """ SAL-008 pause and resume the vm with type default.

        **Test Scenario:**
 
        #. Create a vm[vm1]  on node, should succeed.
        #. Pause [vm1], should succeed.
        #. Check that [vm1] has been paused successfully.
        #. Resume [vm1], should succeed.
        #. Check that [vm1] is runninng and can access it again.
        """
        if os_type == 'zero-os':
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/102')

        self.log("Create a vm[vm1], should succeed.")
        self.create_booted_vm(os_type)

        self.log("Pause [vm1], should succeed.")
        self.created_vm.pause()

        self.log("Check that [vm1] has been paused successfully.")
        self.assertEqual(self.created_vm.info['state'], 'paused')
        result1 = self.execute_command(ip=self.vm_zt_ip, cmd='pwd')
        self.assertTrue(result1.returncode)

        self.log("Resume [vm1], should succeed.")
        self.created_vm.resume()

        self.log("Check that [vm1] is runninng and can access it again.")
        self.assertEqual(self.created_vm.info['state'], 'running')
        result2 = self.ssh_vm_execute_command(vm_ip=self.vm_zt_ip, cmd='pwd')
        self.assertEqual(result2, '/root')

    @parameterized.expand([["zero-os", "ubuntu"], ["reset", "reboot"]])
    @unittest.skip('https://github.com/threefoldtech/0-core/issues/35')
    def test003_reset_and_reboot_vm(self, os_type, operation):
        """ SAL-009 reset and reboot the vm.

        **Test Scenario:**
 
        #. Create a vm[vm1]  on node, should succeed.
        #. Reset or reboot the vm, should suceeed.
        #. Reboot/reset the VM
        #. Check that [vm] has been rebooted/reset successfully.
        """       
        self.log("Create a vm[vm1], should succeed.")
        self.create_booted_vm(os_type)

        self.log("{} the VM".format(operation))
        if operation == "reset":
            self.created_vm.reset()
        else:
            self.created_vm.reboot()

        self.log("Check that [vm] has been rebooted successfully.")
        reboot_response = self.ssh_vm_execute_command(vm_ip=self.vm_zt_ip, cmd='uptime')
        x = reboot_response.stdout.strip()
        uptime = int(x[x.find('up') + 2 : x.find('min')])
        self.assertAlmostEqual(uptime, 1 , delta=3)
    
    @parameterized.expand(["zero-os", "ubuntu"])
    def test004_shutdown_and_start_vm(self, os_type):
        """ SAL-010
        *Test case for testing shutdown and start vm*

        **Test Scenario:**

        #. Create a vm[vm1], should succeed.
        #. Shutdown [vm1], should succeed.
        #. Check that [vm1] has been forced shutdown successfully.
        #. Start [vm1], should succeed.
        #. Check that [vm1] is running again.
        """
        if os_type == 'zero-os':
            self.skipTest('https://github.com/threefoldtech/jumpscale_lib/issues/102')

        self.log("Create a vm[vm1], should succeed.")
        self.create_booted_vm(os_type)

        self.log("Shutdown [vm1], should succeed.")
        self.created_vm.shutdown()

        self.log("Wait till vm1 shutdown")
        for _ in range(30):
            if not self.created_vm.is_running():
                break
            else:
                time.sleep(5)
        else:
            self.assertFalse(self.created_vm.is_running(),'Take long time to shutdown')
        
        self.log("Check that [vm1] has been forced shutdown successfully.")
        result1 = self.execute_command(ip=self.vm_zt_ip, cmd='pwd')
        self.assertTrue(result1.returncode)

        self.log("Start [vm1], should succeed.")
        self.created_vm.start()
        self.vms.pop()
        self.vms.append(self.created_vm.uuid)

        self.log("Check that [vm1] is running again.")
        result2 = self.ssh_vm_execute_command(vm_ip=self.vm_zt_ip, cmd='pwd')
        self.assertEqual(result2, '/root')
