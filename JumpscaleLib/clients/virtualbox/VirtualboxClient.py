from jumpscale import j

JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
zerotiernetwork = ""
"""

from .VirtualboxVM import VirtualboxVM
from .VirtualboxDisk import VirtualboxDisk


class VirtualboxClient(JSConfigBase):
    """
    info
        https://github.com/SethMichaelLarson/virtualbox-python
    """

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self.vms = {}
        self.disks = {}

        self.logger_enable()

    def _cmd(self, cmd):
        cmd = "VBoxManage %s" % cmd
        self.logger.debug("vb cmd:%s" % cmd)
        rc, out, err = j.sal.process.execute(cmd)
        return out

    @property
    def _p(self):
        return j.tools.prefab.local

    def zos_iso_download(self, zerotierinstance=""):

        if zerotierinstance:
            ztcl = j.clients.zerotier.get(zerotierinstance)
            zerotierid = ztcl.config.data['networkid']
            download = "https://bootstrap.grid.tf/iso/development/%s/development%20debug" % zerotierid
            dest = "/tmp/zos_%s.iso" % zerotierid
        else:
            download = "https://bootstrap.gig.tech/uefi/development/0/development%20debug"
            dest = "/tmp/zos.iso"
        self._p.core.file_download(download, to=dest, overwrite=False)
        self.logger.info("iso downloaded ok.")
        return dest

    def vm_list(self):
        result = {}
        res = self._cmd("list vms")
        if res.strip() == "":
            return {}
        for l in res.split("\n"):
            if l.strip() is "":
                continue
            if "{" not in l:
                continue
            pre, post = l.split("{", 1)
            guid = post.split("}", 1)[0]
            name = pre.strip().strip("\"").strip()
            result[name.lower().strip()] = guid.strip()

        return result

    def vms_get(self):
        res = []
        for key, d in self.vm_list().items():
            res.append(self.vm_get(name=key))
        return res

    def vdisk_list(self):
        out = self._cmd("list hdds -l -s")
        return self._parse(out, identifier="UUID:")

    def _parse(self, txt, identifier="UUID:"):
        res = []
        for l in txt.split("\n"):
            if l.startswith(identifier):
                res.append({})
                last = res[-1]
            if ":" in l:
                pre, post = l.split(":", 1)
                name = pre.strip().strip("'").strip()
                last[name.lower().strip()] = post.strip().strip("'").strip()
        return res

    def hostonlyifs_list(self):
        out = self._cmd("list hostonlyifs -l -s")
        return self._parse(out, identifier="Name:")

    def vdisks_get(self):
        res = []
        for disk in self.vdisk_list():
            res.append(self.disk_get(path=disk["location"]))
        return res

    def reset_all(self):
        for vm in self.vms_get():
            vm.stop()
            from time import sleep
            sleep(5)
            vm.delete()
        for disk in self.vdisks_get():
            disk.delete()

    def reset(self, name):
        vm = self.vm_get(name)
        vm.stop()
        from time import sleep
        sleep(5)
        vm.delete()

    def vm_get(self, name):
        if name not in self.vms:
            self.vms[name] = VirtualboxVM(name=name, client=self)
        return self.vms[name]

    def disk_get(self, path):
        if path not in self.disks:
            self.disks[path] = VirtualboxDisk(client=self, path=path)
        return self.disks[path]

    def vm_create(self, name="test", reset=True, isopath="", redis_port="4444"):
        vm = self.vm_get(name)
        vm.create(isopath=isopath, reset=reset, redis_port=redis_port)
        return vm

    def zos_create(self, name="test", zerotierinstance="", redis_port="4444"):
        isopath = self.zos_iso_download(zerotierinstance)
        return self.vm_create(name, isopath=isopath, redis_port=redis_port)
