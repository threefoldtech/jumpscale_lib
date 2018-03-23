from js9 import j


JSBASE = j.application.jsbase_get_class()
from .VirtualboxDisk import VirtualboxDisk

class VirtualboxVM(JSBASE):
    def __init__(self,name,client):
        JSBASE.__init__(self)
        self.client = client
        self.name = name
        self._guid = ""

    def _cmd(self,cmd):
        cmd = "VBoxManage %s"%cmd
        self.logger.debug("vb cmd:%s"%cmd)
        rc,out,err=j.sal.process.execute(cmd)
        return out

    def _cmd2(self,cmd):
        cmd = "VBoxManage modifyvm %s %s"%(self.name,cmd)
        self.logger.debug("vb2 cmd:%s"%cmd)
        rc,out,err=j.sal.process.execute(cmd)
        return out
        

    def delete(self):
        while self.name in self.client.vm_list():
            self._cmd("unregistervm %s --delete"%self.name)
        p="%s/%s.vbox"%(self.path,self.name)
        if j.sal.fs.exists(p):
            j.sal.fs.remove(p)
        p="%s/%s.vbox-prev"%(self.path,self.name)
        if j.sal.fs.exists(p):
            j.sal.fs.remove(p)

    @property
    def path(self):
        return "%s/VirtualBox VMs/%s/"%(j.dirs.HOMEDIR,self.name)

    @property
    def guid(self):
        print("guid")
        from IPython import embed;embed(colors='Linux')
        s


    @property
    def disks(self):
        res= []
        for item in self.client.vdisks_get():
            if item.vm == self:
                res.append(item.vm)        
        return res
        print("vm disks")
        from IPython import embed;embed(colors='Linux')
        s


    def disk_create(self,name="main",size=10000,reset=True):
        path="%s/%s.vdi"%(self.path,name)
        d=self.client.disk_get(path=path)
        d.create(size=size,reset=reset)
        return d

                
    def create(self,reset=True,isopath="",datadisksize=10000,memory=1000):
        if reset:
            self.delete()
        cmd = "createvm --name %s  --ostype \"Linux_64\" --register"%(self.name)
        self._cmd(cmd)
        self._cmd2("--memory=%s "%(memory)
        self._cmd2("--ioapic on")
        self._cmd2("--boot1 dvd --boot2 disk")
        # self._cmd2("--nic1 bridged --bridgeadapter1 e1000g0")

        if datadisksize>0:
            disk = self.disk_create(size=datadisksize,reset=reset)
            cmd = "storagectl %s --name \"SATA Controller\" --add sata  --controller IntelAHCI"%self.name
            self._cmd(cmd)
            cmd = "storageattach %s --storagectl \"SATA Controller\" --port 0 --device 0 --type hdd --medium '%s'"%(self.name,disk.path)
            self._cmd(cmd)

    
        if isopath:
            cmd = "storagectl %s --name \"IDE Controller\" --add ide"%self.name
            self._cmd(cmd)
            cmd = "storageattach %s --storagectl \"IDE Controller\" --port 0 --device 0 --type dvddrive --medium %s"%(self.name,isopath)
            self._cmd(cmd)

    def __repr__(self):
        return "vm: %-20s%s"%(self.name,self.path)

    __str__ = __repr__

            