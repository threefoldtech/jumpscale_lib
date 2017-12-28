
from js9 import j
import os
import sys

from .GiteaClient import GiteaClient

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
        JSConfigBase.__init__(self)
        self._CHILDCLASS = GiteaClient

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def generate(self):
        """
        generate the client out of the raml specs
        """
        c = j.tools.raml.get(self._path)
        c.client_python_generate()

    def test(self):
        self.generate()
        cl = self.get() #now not workgin something wrong with generation?

        # @todo: do some code with some basic tests e.g. list the repositories