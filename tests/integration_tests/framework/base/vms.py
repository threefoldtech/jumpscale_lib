from jumpscale import j
import copy
from termcolor import colored


class VM:

    def __init__(self, node, data={}):
        self.data = data
        self.node_sal = node
        self.vm_sal = None

    @property
    def _vm_sal(self):
        data = self.data.copy()
        return self.node_sal.primitives.from_dict('vm', data)

    def update_ipxeurl(self, url):
        self.data['ipxeUrl'] = url

    def generate_identity(self):
        self.data['ztIdentity'] = self.node_sal.generate_zerotier_identity()
        return self.data['ztIdentity']

    def install(self):
        print(colored('Installing vm %s' % self.data["name"], 'white'))
        self.vm_sal = self.vm_sal or self._vm_sal
        self.vm_sal.deploy()
        self.data['uuid'] = self.vm_sal.uuid
        self.data['ztIdentity'] = self.vm_sal.zt_identity

    def zt_identity(self):
        return self.data['ztIdentity']

    def uninstall(self):
        print(colored('Uninstalling vm %s' % self.data["name"], 'white'))
        self.vm_sal.destroy()

    def shutdown(self, force=False):
        print(colored('Shuting down vm %s' % self.data["name"], 'white'))
        if force is False:
            self.vm_sal.shutdown()
        else:
            self.vm_sal.destroy()

    def pause(self):
        print(colored('Pausing vm %s' % self.data["name"], 'white'))
        self.vm_sal.pause()

    def start(self):
        print(colored('Starting vm {}'.format(self.data["name"]), 'white'))
        self.vm_sal.start()

    def resume(self):
        print(colored('Resuming vm %s' % self.data["name"],'white')) 
        self.vm_sal.resume()
     
    def reboot(self):
        print(colored('Rebooting vm %s' % self.data["name"], 'white'))
        self.vm_sal.reboot()

    def reset(self):
        print(colored('Resetting vm %s' % self.data["name"],'white'))
        self.vm_sal.reset()

    def info(self, timeout=None, data=None):
        return self.vm_sal.info

    def enable_vnc(self):
        print(colored('Enable vnc for vm %s' % self.data["name"], 'white'))
        self.vm_sal.enable_vnc()

    def disable_vnc(self):
        print(colored('Disable vnc for vm %s' % self.data["name"], 'white'))
        self.vm_sal.disable_vnc()

    def generate_vm_sal(self):
        self.vm_sal = self._vm_sal
    
    def add_port(self, name, source, target):
        self.vm_sal.ports.add(name=name, source=source, target=target)

    def del_port(self, name):
        self.vm_sal.ports.add(name=name)
    
    def list_port(self):
        return self.vm_sal.ports.list()
    
    def is_running(self):
        return self.vm_sal.is_running()

    def add_disk(self, name_or_disk, url=None, mountpoint=None, filesystem=None, label=None):
        self.vm_sal.disks.add(name_or_disk=name_or_disk, url=url, mountpoint=mountpoint, filesystem=filesystem, label=label)
    
    def remove_disk(self, name):
        self.vm_sal.disks.remove(name)
    
    def list_disk(self, name):
        return self.vm_sal.disks.list()

    def update_disks(self):
        self.vm_sal.update_disks()

    def add_nics(self, type_, name, networkid=None):
        self.vm_sal.nics.add(type_=type_, name=name, networkid=networkid)

    def add_zerotier_nics(self, network, name=None):
        self.vm_sal.nics.add_zerotier(name=name, network=network)

    def remove_nics(self, item):
        self.vm_sal.nics.remove(item=item)

    def list_nics(self):
        return self.vm_sal.nics.list()

    def change_params(self, param, value):
        setattr(self.vm_sal, param, value)

    def add_mount(self, name, source, target):
        self.vm_sal.mounts.add(name=name, sourcepath=source, targetpath=target)
    
    def remove_mount(self, item):
        self.vm_sal.mounts.remove(item=item)

    def list_mount(self):
        return self.vm_sal.mounts.list()

    def add_config(self, name, path, content):
        self.vm_sal.configs.add(name=name, path=path, content=content)
    
    def remove_config(self, item):
        self.vm_sal.configs.remove(item=item)

    def list_config(self):
        return self.vm_sal.configs.list()