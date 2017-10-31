from js9 import j
import copy
import tarfile
import time
from io import BytesIO


class Container:
    """Docker Container"""

    def __init__(self, obj, client):
        """
        Container object instance.

        @param name str: name of conainter.
        @param id  int: id of container.
        @param client obj(docker.Client()): client object from docker library.
        """

        self.client = client
        self.logger = j.logger.get('docker_container')

        self.obj=obj
        self.name = obj.name
        self.id = obj.id

        self._ssh_port = None
        self._sshclient = None
        self._prefab = None
        self._executor = None

    @property
    def ssh_port(self):
        if self._ssh_port is None:
            self._ssh_port = self.getPubPortForInternalPort(22)
        return self._ssh_port

    @property
    def image(self):
        return self.info["Config"]["Image"]

    @property
    def sshclient(self):
        if self._sshclient is None:
            self.executor.sshclient.get(
                addr=self.host,
                port=self.ssh_port,
                login='root',
                passwd="gig1234",
                timeout=10,
                usecache=False,
                allow_agent=True)
            self._sshclient = self.executor.sshclient
        return self._sshclient

    @property
    def executor(self):
        if self._executor is None:
            self._executor = j.tools.executor.getSSHBased(
                addr=self.host, port=self.ssh_port, login='root', passwd="gig1234", usecache=False, allow_agent=True)
        return self._executor

    @property
    def mounts(self):
        res=[]
        mountinfo=self.info["Mounts"]
        for item in mountinfo:
            res.append((item["Source"],item["Destination"]))
        return res

    @property
    def status(self):
        return self.info["State"]["Status"]
        # if self.info["State"]["Running"]:
        #     return "running"
        # if self.info["State"]["Restarting"]:
        #     return "restarting"
        # if self.info["State"]["Paused"]:
        #     return "paused"
        # return "error"

    def prefab(self):
        if self._prefab is None:
            self._prefab = j.tools.prefab.get(self.executor, usecache=False)
        return self._prefab

    def run(self, cmd):
        """
        Run Docker exec with cmd.
        @param  cmd str: cmd to be executed will default run in bash
        """
        cmd2 = "docker exec -i -t %s %s" % (self.name, cmd)
        j.sal.process.executeWithoutPipe(cmd2)

    def execute(self, path):
        """
        execute file in docker
        """
        self.copy(path, path)
        self.run("chmod 770 %s;%s" % (path, path))

    @property
    def info(self):
        return self.obj.attrs

    def isRunning(self):
        """
        Check conainter is running.
        """
        return self.info["State"]["Running"] is True

    def getIp(self):
        """
        Return ip of docker on hostmachine.
        """
        return self.info['NetworkSettings']['IPAddress']

    def getPubPortForInternalPort(self, port):
        """
        Return public port that is forwarded to a port inside docker,
        this will only work if container has port forwarded the ports during
        run time.

        @param port int: port number inside docker to use.
        """

        if not self.info["NetworkSettings"]["Ports"] is None:
            for key, portsDict in self.info["NetworkSettings"]["Ports"].items():
                if key.startswith(str(port)) and portsDict is not None:
                    # if "PublicPort" not in port2:
                    #     raise j.exceptions.Input("cannot find publicport for ssh?")
                    portsfound = [int(item['HostPort']) for item in portsDict]
                    if len(portsfound) > 0:
                        return portsfound[0]

        if self.isRunning() is False:
            raise j.exceptions.RuntimeError(
                "docker %s is not running cannot get pub port." % self)

        raise j.exceptions.Input("cannot find publicport for ssh?")

    def pushSSHKey(self, keyname="", sshpubkey="", generateSSHKey=True):
        """
        Push ssh keys onto container, the params are mutually exclusive.

        @param keyname str: path to key or just keyname in /root/.ssh/keyname.
        @param sshpubkey str: actual key content.
        @param generateSSHKey bool: generate a key called docker_default.
        """
        keys = set()

        home = j.tools.prefab.local.bash.home
        user_info = [j.tools.prefab.local.system.user.check(user) for user in j.tools.prefab.local.system.user.list()]
        user = [i['name'] for i in user_info if i['home'] == home]
        user = user[0] if user else 'root'

        if sshpubkey != "" and sshpubkey is not None:
            key = sshpubkey
        else:
            if not j.clients.ssh.ssh_agent_available():
                j.clients.ssh.start_ssh_agent()

            if keyname != "" and keyname is not None:
                key = j.clients.ssh.SSHKeyGetFromAgentPub(keyname)
            else:
                key = j.clients.ssh.SSHKeyGetFromAgentPub("docker_default", die=False)
                if key is None:
                    dir = j.tools.path.get('%s/.ssh' % home)
                    if dir.listdir("docker_default.pub") == []:
                        # key does not exist, lets create one
                        j.tools.prefab.local.system.ssh.keygen(user=user, name="docker_default")
                    key = j.sal.fs.readFile(
                        filename="%s/.ssh/docker_default.pub" % home)
                    # load the key
                    j.tools.executorLocal.execute(
                        "ssh-add %s/.ssh/docker_default" % home)

        j.sal.fs.writeFile(filename="%s/.ssh/known_hosts" % home, contents="")

        if key is None or key.strip() == "":
            raise j.exceptions.Input("ssh key cannot be empty (None)")

        self.prefab.system.ssh.authorize("root", key)

        # IS THERE A REASON TO DO IT THE LONG WAY BELOW?
        # key_tarstream = BytesIO()
        # key_tar = tarfile.TarFile(fileobj=key_tarstream, mode='w')
        # tarinfo = tarfile.TarInfo(name='authorized_keys')
        # tarinfo.size = len(key)
        # tarinfo.mtime = time.time()
        # tarinfo.mode = 0o600
        # key_tar.addfile(tarinfo, BytesIO(key.encode()))
        # key_tar.close()
        #
        # key_tarstream.seek(0)
        # exec_id = self.client.exec_create(self.id, "mkdir -p /root/.ssh/")
        # self.client.exec_start(exec_id['Id'])
        # self.client.put_archive(self.id, '/root/.ssh/', data=key_tarstream)

        return list(keys)


    def destroy(self):
        """
        Stop and remove container.
        """
        self.cleanAysfs()

        try:
            if self.isRunning():
                self.client.kill(self.id)
            self.client.remove_container(self.id)
        except Exception as e:
            self.logger.error("could not kill:%s" % self.id)
        finally:
            if self.id in j.sal.docker._containers:
                del j.sal.docker._containers[self.id]

    def stop(self):
        """
        Stop running instance of container.
        """
        self.cleanAysfs()
        self.client.kill(self.id)

    def restart(self):
        """
        Restart isntance of the container.
        """
        self.client.restart(self.id)

    def commit(self, imagename, msg="", delete=True, force=False, push=False, **kwargs):
        """
        imagename: name of the image to commit. e.g: jumpscale/myimage
        delete: bool, delete current image before doing commit
        force: bool, force delete
        """
        previous_timeout = self.client.timeout
        self.client.timeout = 3600

        if delete:
            res = j.sal.docker.client.images(imagename)
            if len(res) > 0:
                self.client.remove_image(imagename, force=force)
        self.client.commit(self.id, imagename, message=msg, **kwargs)

        self.client.timeout = previous_timeout

        if push:
            j.sal.docker.push(imagename)



    def __str__(self):
        return "docker:%s" % self.name

    __repr__ = __str__

    # def setHostName(self,name,hostname):
    #     return # TODO:
    #     c=self.getSSH(name)
    #     # TODO:
    #     # c.run("echo '%s' > /etc/hostname;hostname %s"%(hostname,hostname))
    #

    # def _btrfsExecute(self,cmd):
    #     cmd="btrfs %s"%cmd
    #     print(cmd)
    #     return self._execute(cmd)

    # def btrfsSubvolList(self):
    #     raise j.exceptions.RuntimeError("not implemented")
    #     out=self._btrfsExecute("subvolume list %s"%self.basepath)
    #     res=[]
    #     for line in out.split("\n"):
    #         if line.strip()=="":
    #             continue
    #         if line.find("path ")!=-1:
    #             path=line.split("path ")[-1]
    #             path=path.strip("/")
    #             path=path.replace("lxc/","")
    #             res.append(path)
    #     return res

    # def btrfsSubvolNew(self,name):
    #     raise j.exceptions.RuntimeError("not implemented")
    #     if not self.btrfsSubvolExists(name):
    #         cmd="subvolume create %s/%s"%(self.basepath,name)
    #         self._btrfsExecute(cmd)

    # def btrfsSubvolCopy(self,nameFrom,NameDest):
    #     raise j.exceptions.RuntimeError("not implemented")
    #     if not self.btrfsSubvolExists(nameFrom):
    #         raise j.exceptions.RuntimeError("could not find vol for %s"%nameFrom)
    #     if j.sal.fs.exists(path="%s/%s"%(self.basepath,NameDest)):
    #         raise j.exceptions.RuntimeError("path %s exists, cannot copy to existing destination, destroy first."%nameFrom)
    #     cmd="subvolume snapshot %s/%s %s/%s"%(self.basepath,nameFrom,self.basepath,NameDest)
    #     self._btrfsExecute(cmd)

    # def btrfsSubvolExists(self,name):
    #     raise j.exceptions.RuntimeError("not implemented")
    #     subvols=self.btrfsSubvolList()
    #     # print subvols
    #     return name in subvols

    # def btrfsSubvolDelete(self,name):
    #     raise j.exceptions.RuntimeError("not implemented")
    #     if self.btrfsSubvolExists(name):
    #         cmd="subvolume delete %s/%s"%(self.basepath,name)
    #         self._btrfsExecute(cmd)
    #     path="%s/%s"%(self.basepath,name)
    #     if j.sal.fs.exists(path=path):
    #         j.sal.fs.removeDirTree(path)
    #     if self.btrfsSubvolExists(name):
    #         raise j.exceptions.RuntimeError("vol cannot exist:%s"%name)

    # def getProcessList(self, stdout=True):
    #     """
    #     @return [["$name",$pid,$mem,$parent],....,[$mem,$cpu]]
    #     last one is sum of mem & cpu
    #     """
    #     raise j.exceptions.RuntimeError("not implemented")
    #     pid = self.getPid()
    #     children = list()
    #     children = self._getChildren(pid, children)
    #     result = list()
    #     pre = ""
    #     mem = 0.0
    #     cpu = 0.0
    #     cpu0 = 0.0
    #     prevparent = ""
    #     for child in children:
    #         if child.parent.name != prevparent:
    #             pre += ".."
    #             prevparent = child.parent.name
    #         # cpu0=child.get_cpu_percent()
    #         mem0 = int(round(child.get_memory_info().rss / 1024, 0))
    #         mem += mem0
    #         cpu += cpu0
    #         if stdout:
    #             self.logger.info(("%s%-35s %-5s mem:%-8s" % (pre, child.name, child.pid, mem0)))
    #         result.append([child.name, child.pid, mem0, child.parent.name])
    #     cpu = children[0].get_cpu_percent()
    #     result.append([mem, cpu])
    #     if stdout:
    #         self.logger.info(("TOTAL: mem:%-8s cpu:%-8s" % (mem, cpu)))
    #     return result
