import libvirt
from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader, FileSystemLoader
import os
import time
import shutil
import random
from qcow2 import Qcow2
from Jumpscale import j
import atexit

LOCKCREATED = 1
LOCKREMOVED = 2
NOLOCK = 3
LOCKEXIST = 4

JSBASE = j.application.JSBaseClass


class LibvirtUtil(JSBASE):

    def __init__(self, host='localhost'):
        self._host = host
        self.open()
        atexit.register(self.close)
        self.basepath = '/mnt/vmstor/kvm'
        self.templatepath = '/mnt/vmstor/kvm/images'
        self.env = Environment(loader=FileSystemLoader(
            j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'templates')))
        JSBASE.__init__(self)

    def open(self):
        uri = None
        if self._host != 'localhost':
            uri = 'qemu+ssh://%s/system' % self._host
        self.connection = libvirt.open(uri)
        self.readonly = libvirt.openReadOnly(uri)

    def close(self):
        def close(con):
            if con:
                try:
                    con.close()
                except BaseException:
                    pass
        close(self.connection)
        close(self.readonly)

    def _get_domain(self, id):
        try:
            domain = self.connection.lookupByName(id)
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                return None
        return domain

    def create(self, id, xml):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't start a locked machine")
        domain = self._get_domain(id)
        if not domain and xml:
            domain = self.connection.defineXML(xml)
        if domain.state(0)[0] == libvirt.VIR_DOMAIN_RUNNING:
            return True
        return domain.create() == 0

    def shutdown(self, id):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't stop a locked machine")
        domain = self._get_domain(id)
        if domain.state(0)[0] in [libvirt.VIR_DOMAIN_SHUTDOWN, libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED]:
            return True
        return domain.shutdown() == 0

    def suspend(self, id):
        domain = self._get_domain(id)
        if domain.state(0)[0] == libvirt.VIR_DOMAIN_PAUSED:
            return True
        return domain.suspend() == 0

    def resume(self, id):
        domain = self._get_domain(id)
        if domain.state(0)[0] == libvirt.VIR_DOMAIN_RUNNING:
            return True
        return domain.resume() == 0

    def backup_machine_to_filesystem(self, machineid, backuppath):
        from shutil import make_archive
        if self.isCurrentStorageAction(machineid):
            raise Exception("Can't delete a locked machine")
        domain = self.connection.lookupByUUIDString(machineid)
        diskfiles = self._get_domain_disk_file_names(domain)
        if domain.state(0)[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            domain.destroy()
        for diskfile in diskfiles:
            if os.path.exists(diskfile):
                try:
                    vol = self.connection.storageVolLookupByPath(diskfile)
                except BaseException:
                    continue
                poolpath = os.path.join(self.basepath, domain.name())
                if os.path.exists(poolpath):
                    archive_name = os.path.join(
                        backuppath, 'vm-%04x' % machineid)
                    root_dir = poolpath
                    make_archive(archive_name, gztar, root_dir)
        return True

    def delete_machine(self, id):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't delete a locked machine")

        domain = self._get_domain(id)
        if domain:
            if domain.state(0)[0] != libvirt.VIR_DOMAIN_SHUTOFF:
                domain.destroy()
            domain.undefineFlags(
                libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)

        poolpath = os.path.join(self.basepath, id)
        try:
            diskpool = self.connection.storagePoolLookupByName(id)
            for vol in diskpool.listAllVolumes():
                vol.delete()
            diskpool.destroy()
        except BaseException:
            pass
        if os.path.exists(poolpath):
            shutil.rmtree(poolpath)

        return True

    def _get_domain_disk_file_names(self, dom):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        else:
            xml = ElementTree.fromstring(dom.XMLDesc(0))
            disks = xml.findall('devices/disk')
            diskfiles = list()
        for disk in disks:
            if disk.attrib['device'] == 'disk' or disk.attrib['device'] == 'cdrom':
                source = disk.find('source')
                if source is not None:
                    if disk.attrib['device'] == 'disk':
                        if 'dev' in source.attrib:
                            diskfiles.append(source.attrib['dev'])
                        if 'file' in source.attrib:
                            diskfiles.append(source.attrib['file'])
                    if disk.attrib['device'] == 'cdrom':
                        diskfiles.append(source.attrib['file'])
        return diskfiles

    def check_disk(self, diskxml):
        return True

    def memory_usage(self):
        ids = self.readonly.listDomainsID()
        hostmem = self.readonly.getInfo()[1]
        totalmax = 0
        totalrunningmax = 0
        for id in ids:
            dom = self.readonly.lookupByID(id)
            machinestate, maxmem, mem = dom.info()[0:3]
            totalmax += maxmem / 1000
            if machinestate == libvirt.VIR_DOMAIN_RUNNING:
                totalrunningmax += maxmem / 1000
        return (hostmem, totalmax, totalrunningmax)

    def check_machine(self, machinexml):
        xml = ElementTree.fromstring(machinexml)
        memory = int(xml.find('memory').text)
        hostmem, totalmax, totalrunningmax = self.memory_usage()
        if (totalrunningmax + memory) > (hostmem - 1024):
            return False
        return True

    def _snapshot(self, id, xml, snapshottype):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't snapshot a locked machine")
        domain = self._get_domain(id)
        flags = 0 if snapshottype == 'internal' else libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY
        snap = domain.snapshotCreateXML(xml, flags)
        return {'name': snap.getName(), 'xml': snap.getXMLDesc()}

    def listSnapshots(self, id):
        domain = self._get_domain(id)
        results = list()
        for snapshot in domain.listAllSnapshots():
            xml = ElementTree.fromstring(snapshot.getXMLDesc())
            snap = {'name': xml.find('name').text,
                    'epoch': int(xml.find('creationTime').text)}
            results.append(snap)
        return results

    def deleteVolume(self, path):
        vol = self.connection.storageVolLookupByPath(path)
        return vol.delete(0)

    def getSnapshot(self, domain, name):
        domain = self._get_domain(domain)
        snap = domain.snapshotLookupByName('name')
        return {'name': snap.getName(), 'epoch': snap.getXMLDesc()}

    def _isRootVolume(self, domain, file):
        diskfiles = self._getDomainDiskFiles(domain)
        if file in diskfiles:
            return True
        return False

    def _renameSnapshot(self, id, name, newname):
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        xml = snapshot.getXMLDesc()
        newxml = xml.replace('<name>%s</name>' %
                             name, '<name>%s</name>' % newname)
        domain.snapshotCreateXML(
            newxml, (libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_REDEFINE or libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY))
        snapshot.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        return True

    def deleteSnapshot(self, id, name):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't delete a snapshot from a locked machine")
        newname = '%s_%s' % (name, 'DELETING')
        self._renameSnapshot(id, name, newname)
        name = newname
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        snapshotfiles = self._getSnapshotDisks(id, name)
        volumes = []
        todelete = []
        for snapshotfile in snapshotfiles:
            is_root_volume = self._isRootVolume(
                domain, snapshotfile['file'].path)
            if not is_root_volume:
                self.logger.debug('Blockcommit from %s to %s' % (snapshotfile[
                      'file'].path, snapshotfile['file'].backing_file_path))
                result = domain.blockCommit(snapshotfile['name'], snapshotfile[
                                            'file'].backing_file_path, snapshotfile['file'].path)
                todelete.append(snapshotfile['file'].path)
                volumes.append(snapshotfile['name'])
            else:
                # we can't use blockcommit on topsnapshots
                new_base = Qcow2(
                    snapshotfile['file'].backing_file_path).backing_file_path
                todelete.append(snapshotfile['file'].backing_file_path)
                if not new_base:
                    continue
                    self.logger.debug('Blockrebase from %s' % new_base)
                flags = libvirt.VIR_DOMAIN_BLOCK_REBASE_COPY | libvirt.VIR_DOMAIN_BLOCK_REBASE_REUSE_EXT | libvirt.VIR_DOMAIN_BLOCK_REBASE_SHALLOW
                result = domain.blockRebase(
                    snapshotfile['name'], new_base, flags)
                volumes.append(snapshotfile['name'])

        while not self._block_job_domain_info(domain, volumes):
            time.sleep(0.5)

        # we can undefine the snapshot
        snapshot.delete(flags=libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        for disk in todelete:
            if os.path.exists(disk):
                os.remove(disk)
        return True

    def isCurrentStorageAction(self, domainid):
        domain = self._get_domain(domainid)
        if not domain:
            return False
        # at this moment we suppose the machine is following the default naming
        # of disks
        if domain.state()[0] not in [libvirt.VIR_DOMAIN_SHUTDOWN,
                                     libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED]:
            status = domain.blockJobInfo('vda', 0)
            if 'cur' in status:
                return True
        # check also that there is no qemu-img job running
        if self.isLocked(domainid):
            return True
        return False

    def _getLockFile(self, domainid):
        LOCKPATH = '%s/domain_locks' % j.dirs.VARDIR
        if not j.sal.fs.exists(LOCKPATH):
            j.sal.fs.createDir(LOCKPATH)
        lockfile = '%s/%s.lock' % (LOCKPATH, domainid)
        return lockfile

    def _lockDomain(self, domainid):
        if self.isLocked(domainid):
            return LOCKEXIST
        j.sal.fs.writeFile(self._getLockFile(domainid), str(time.time()))
        return LOCKCREATED

    def _unlockDomain(self, domainid):
        if not self.isLocked(domainid):
            return NOLOCK
        j.sal.fs.remove(self._getLockFile(domainid))
        return LOCKREMOVED

    def isLocked(self, domainid):
        if j.sal.fs.exists(self._getLockFile(domainid)):
            return True
        else:
            return False

    def _block_job_domain_info(self, domain, paths):
        for path in paths:
            done = self._block_job_info(domain, path)
            if not done:
                return False
        return True

    def _block_job_info(self, domain, path):
        status = domain.blockJobInfo(path, 0)
        self.logger.debug(status)
        try:
            cur = status.get('cur', 0)
            end = status.get('end', 0)
            if cur == end:
                return True
        except Exception:
            return True
        else:
            return False

    def rollbackSnapshot(self, id, name, deletechildren=True):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't rollback a locked machine")
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        snapshotdomainxml = ElementTree.fromstring(snapshot.getXMLDesc(0))
        domainxml = snapshotdomainxml.find('domain')
        newxml = ElementTree.tostring(domainxml)
        self.connection.defineXML(newxml)
        if deletechildren:
            children = snapshot.listAllChildren(1)
            for child in children:
                snapshotfiles = self._getSnapshotDisks(id, child.getName())
                for snapshotfile in snapshotfiles:
                    os.remove(snapshotfile['file'].path)
                child.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
            snapshotfiles = self._getSnapshotDisks(id, name)
            for snapshotfile in snapshotfiles:
                os.remove(snapshotfile['file'].path)
            snapshot.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        return True

    def _clone(self, id, name, clonefrom):
        domain = self.connection.lookupByUUIDString(id)
        domainconfig = domain.XMLDesc()
        name = '%s_%s.qcow2' % (name, time.time())
        destination_path = os.path.join(self.templatepath, name)
        if domain.state()[0] in [
                libvirt.VIR_DOMAIN_SHUTDOWN,
                libvirt.VIR_DOMAIN_SHUTOFF,
                libvirt.VIR_DOMAIN_CRASHED,
                libvirt.VIR_DOMAIN_PAUSED] or not self._isRootVolume(
                domain,
                clonefrom):
            if not self.isLocked(id):
                lock = self._lockDomain(id)
                if lock != LOCKCREATED:
                    raise Exception('Failed to create lock: %s' % str(lock))
            else:
                raise Exception("Can't perform this action on a locked domain")
            q2 = Qcow2(clonefrom)
            try:
                q2.export(destination_path)
            finally:
                if self.isLocked(id):
                    self._unlockDomain(id)
        else:
            domain.undefine()
            try:
                domain.blockRebase(clonefrom, destination_path,
                                   0, libvirt.VIR_DOMAIN_BLOCK_REBASE_COPY)
                rebasedone = False
                while not rebasedone:
                    rebasedone = self._block_job_info(domain, clonefrom)
                domain.blockJobAbort(clonefrom, 0)
            except BaseException:
                self.connection.defineXML(domainconfig)
                raise
            self.connection.defineXML(domainconfig)
        return destination_path

    def _getImageId(self, path):
        return j.data.hash.sha1(path)

    def exportToTemplate(self, id, name, clonefrom):
        if self.isCurrentStorageAction(id):
            raise Exception("Can't export a locked machine")
        domain = self.connection.lookupByUUIDString(id)
        if not clonefrom:
            domaindisks = self._getDomainDiskFiles(domain)
            if len(domaindisks) > 0:
                clonefrom = domaindisks[0]
            else:
                raise Exception('Node image found for this machine')
        else:
            snapshotfiles = self._getSnapshotDisks(id, name)
            # we just take the first one at this moment
            if len(snapshotfiles) > 0:
                clonefrom = snapshotfiles[0]['file'].backing_file_path
            else:
                raise Exception('No snapshot found')
        destination_path = self._clone(id, name, clonefrom)
        imageid = self._getImageId(destination_path)
        return imageid, destination_path

    def create_disk(self, diskxml, poolname):
        pool = self._get_pool(poolname)
        pool.createXML(diskxml, 0)
        return True

    def _getSnapshotDisks(self, id, name):
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        snapshotxml = ElementTree.fromstring(snapshot.getXMLDesc(0))
        snapshotfiles = []
        disks = snapshotxml.findall('disks/disk')
        for disk in disks:
            source = disk.find('source')
            if source is not None and disk.attrib['snapshot'] == 'external':
                snapshotfiles.append(
                    {'name': disk.attrib['name'], 'file': Qcow2(source.attrib['file'])})
        return snapshotfiles

    def _get_pool(self, poolname):
        self.check_storagepool(poolname)
        storagepool = self.connection.storagePoolLookupByName(poolname)
        return storagepool

    def check_storagepool(self, poolname):
        if poolname not in self.connection.listStoragePools():
            poolpath = os.path.join(self.basepath, poolname)
            if not os.path.exists(poolpath):
                os.makedirs(poolpath)
                cmd = 'chattr +C %s ' % poolpath
                j.sal.process.execute(
                    cmd, die=False, showout=False, useShell=False, ignoreErrorOutput=False)
            pool = self.env.get_template('pool.xml').render(
                poolname=poolname, basepath=self.basepath)
            self.connection.storagePoolCreateXML(pool, 0)
        return True

    def create_machine(self, machinexml):
        domain = self.connection.defineXML(machinexml)
        domain.create()
        return self._to_node(domain)

    def _to_node(self, domain):
        state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
        locked = self.isCurrentStorageAction(domain.UUIDString())
        extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(
        ), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time, 'locked': locked}
        return {'id': domain.UUIDString(), 'name': domain.name(), 'state': state,
                'extra': extra, 'XMLDesc': domain.XMLDesc(0)}

    def _to_node_list(self, domain):
        state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
        extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(
        ), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time}
        return {'id': domain.UUIDString(), 'name': domain.name(), 'state': state, 'extra': extra}

    def get_domain(self, uuid):
        domain = self.connection.lookupByUUIDString(uuid)
        return self._to_node(domain)

    def list_domains(self):
        nodes = []
        for x in self.connection.listAllDomains(0):
            nodes.append(self._to_node_list(x))
        return nodes

    def _getDomainDiskFiles(self, domain):
        xml = ElementTree.fromstring(domain.XMLDesc(0))
        disks = xml.findall('devices/disk')
        diskfiles = list()
        for disk in disks:
            if disk.attrib['device'] == 'disk':
                source = disk.find('source')
                if source is not None:
                    if 'dev' in source.attrib:
                        diskfiles.append(source.attrib['dev'])
                    if 'file' in source.attrib:
                        diskfiles.append(source.attrib['file'])
        return diskfiles

    def _getPool(self, domain):
        # poolname is by definition the machine name
        return self.readonly.storagePoolLookupByName(domain.name())

    def _getTemplatePool(self, templatepoolname=None):
        if not templatepoolname:
            templatepoolname = 'VMStor'
        return self.readonly.storagePoolLookupByName(templatepoolname)

    def createNetwork(self, networkname, bridge):
        networkxml = self.env.get_template('network.xml').render(
            networkname=networkname, bridge=bridge)
        self.connection.networkDefineXML(networkxml)
        nw = self.connection.networkLookupByName(networkname)
        nw.setAutostart(1)
        nw.create()

    def checkNetwork(self, networkname):
        try:
            self.connection.networkLookupByName(networkname)
            return True
        except libvirt.libvirtError as e:
            return False

    def createVMStorSnapshot(self, name):
        vmstor_snapshot_path = j.sal.fs.joinPaths(self.basepath, 'snapshots')
        if not j.sal.fs.exists(vmstor_snapshot_path):
            j.sal.btrfs.subvolumeCreate(self.basepath, 'snapshots')
        vmstorsnapshotpath = j.sal.fs.joinPaths(vmstor_snapshot_path, name)
        j.sal.btrfs.snapshotReadOnlyCreate(self.basepath, vmstorsnapshotpath)
        return True

    def deleteVMStorSnapshot(self, name):
        vmstor_snapshot_path = j.sal.fs.joinPaths(self.basepath, 'snapshots')
        j.sal.btrfs.subvolumeDelete(vmstor_snapshot_path, name)
        return True

    def listVMStorSnapshots(self):
        vmstor_snapshot_path = j.sal.fs.joinPaths(self.basepath, 'snapshots')
        return j.sal.btrfs.subvolumeList(vmstor_snapshot_path)

    def _generateRandomMacAddress(self):
        """Generate a random MAC Address using the VM OUI code"""
        rand_mac_addr = [0x52, 0x54, 0x00, random.randint(
            0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
        return ':'.join(["%02x" % x for x in rand_mac_addr])

    def create_node(self, name, image, bridges=[], size=10, memory=512, cpu_count=1):
        diskname = self._create_disk(name, image, size)
        if not diskname or diskname == -1:
            # not enough free capcity to create a disk on this node
            return -1
        return self._create_node(name, diskname, bridges, size, memory, cpu_count)

    def _create_node(self, name, diskname, bridges, size, memory, cpucount):
        machinetemplate = self.env.get_template("machine.xml")
        macaddresses = [self._generateRandomMacAddress() for bridge in bridges]
        POOLPATH = '%s/%s' % (self.basepath, name)
        machinexml = machinetemplate.render({'machinename': name,
                                             'diskname': diskname,
                                             'memory': memory,
                                             'nrcpu': cpucount,
                                             'poolpath': POOLPATH,
                                             'macaddresses': macaddresses,
                                             'bridges': bridges})
        self.create_machine(machinexml)
        #dnsmasq = DNSMasq()
        #nsid = '%04d' % networkid
        #namespace = 'ns-%s' % nsid
        #config_path = j.sal.fs.joinPaths(j.dirs.VARDIR, 'vxlan',nsid)
        #dnsmasq.setConfigPath(nsid, config_path)
        #dnsmasq.addHost(macaddress, ipaddress,name)

    def _create_disk(self, vm_id, image_name, size=10, disk_role='base'):
        disktemplate = self.env.get_template("disk.xml")
        diskname = vm_id + '-' + disk_role + '.qcow2'
        diskbasevolume = j.sal.fs.joinPaths(
            self.templatepath, image_name, '%s.qcow2' % image_name)
        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
                                       diskbasevolume, 'disksize': size})
        self.create_disk(diskxml, vm_id)
        return diskname

    def snapshot(self, machine_id, name, snapshottype='external'):
        domain = self._get_domain(machine_id)
        diskfiles = self._get_domain_disk_file_names(domain)
        t = int(time.time())
        poolpath = '%s/%s' % (self.basepath, domain.name())
        snapshot_xml = self.env.get_template('snapshot.xml').render(
            name=name, diskfiles=diskfiles, type=snapshottype, time=t, poolpath=poolpath)
        self._snapshot(machine_id, snapshot_xml, snapshottype)
