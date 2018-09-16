from jumpscale import j
import copy
from termcolor import colored


class VM:

    def __init__(self, node, data={}):
        self.data = data
        self.node_sal = node

    @property
    def _vm_sal(self):
        data = self.data.copy()
        return self.node_sal.primitives.from_dict('vm', data)

    def update_ipxeurl(self, url):
        self.data['ipxeUrl'] = url

    def generate_identity(self):
        self.data['ztIdentity'] = self.node_sal.generate_zerotier_identity()
        return self.data['ztIdentity']

    def install(self, vm_sal=None):
        print(colored('Installing vm %s' % self.data["name"], 'white'))
        vm_sal = vm_sal or self._vm_sal
        vm_sal.deploy()
        self.data['uuid'] = vm_sal.uuid
        self.data['ztIdentity'] = vm_sal.zt_identity

    def zt_identity(self):
        return self.data['ztIdentity']

    def uninstall(self):
        print(colored('Uninstalling vm %s' % self.data["name"], 'white'))
        self._vm_sal.destroy()

    def shutdown(self, force=False):
        print(colored('Shuting down vm %s' % self.data["name"], 'white'))
        if force is False:
            self._vm_sal.shutdown()
        else:
            self._vm_sal.destroy()

    def pause(self):
        print(colored('Pausing vm %s' % self.data["name"], 'white'))
        self._vm_sal.pause()

    def start(self):
        print(colored('Starting vm {}'.format(self.data["name"]), 'white'))
        self._vm_sal.start()

    def resume(self):
        print(colored('Resuming vm %s' % self.data["name"],'white')) 
        self._vm_sal.resume()
     
    def reboot(self):
        print(colored('Rebooting vm %s' % self.data["name"], 'white'))
        self._vm_sal.reboot()

    def reset(self):
        print(colored('Resetting vm %s' % self.data["name"],'white'))
        self._vm_sal.reset()

    def enable_vnc(self):
        print(colored('Enable vnc for vm %s' % self.data["name"], 'white'))
        self._vm_sal.enable_vnc()

    def info(self, timeout=None, data=None):
        data = data or self.data
        info = self._vm_sal.info or {}
        nics = copy.deepcopy(data['nics'])
        for nic in nics:
            if nic['type'] == 'zerotier' and nic.get('ztClient') and data.get('ztIdentity'):
                ztAddress = data['ztIdentity'].split(':')[0]
                zclient = j.clients.zerotier.get(nic['ztClient'])
                try:
                    network = zclient.network_get(nic['id'])
                    member = network.member_get(address=ztAddress)
                    member.timeout = None
                    nic['ip'] = member.get_private_ip(timeout)
                except (RuntimeError, ValueError) as e:
                    print(colored('Failed to retreive zt ip: %s', str(e),'red'))

        return {
            'vnc': info.get('vnc'),
            'status': info.get('state', 'halted'),
            'disks': data['disks'],
            'nics': nics,
            'ztIdentity': data['ztIdentity'],
        }

    def disable_vnc(self):
        print(colored('Disable vnc for vm %s' % self.data["name"], 'white'))
        self._vm_sal.disable_vnc()
