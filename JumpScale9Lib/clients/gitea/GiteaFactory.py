
# from .client_shouldnotbehere import client
from js9 import j
import os
import sys
#https://docs.grid.tf/api/swagger example api source

#TODO: make sure full api is working

#TODO: need example code in the client to : set milestones (in line with the legal repo, and calculate automatically)
#TODO: need example code in the client to : set labels (remove ones which should not be there)

#TODO: (phase 2): export/import a full repo (with issues, milestones & labels) (per repo)

JSConfigBase = j.tools.configmanager.base_class_configs
class GiteaFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.gitea"
        self.logger = j.logger.get("j.clients.gitea")
        path="%s/generated"%self._path
        if path not in sys.path:
            sys.path.append(path)
        from .GiteaClient import GiteaClient
        self._CHILDCLASS=GiteaClient 
        JSConfigBase.__init__(self)
               

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def generate(self):
        """
        generate the client out of the raml specs
        """
        c=j.tools.raml.get(self._path)   
        c.client_python_generate()

    def client_get(self,instance="main",data={}):
        """"
        @param data, can be used to not let the client configure automatically
        """
        return GiteaClient(instance=instance,parent=self,data=data)

    def test(self):
        self.generate() #I think there still needs to be a __init__.py in generated directory (needs to be done automatically)
        cl=self.client_get() #now not workgin something wrong with generation?