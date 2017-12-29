
from js9 import j
import os
import sys

from .GiteaClient import GiteaClient

#https://docs.grid.tf/api/swagger example api source


#TODO: (phase 2): export/import a full repo (with issues, milestones & labels) (per repo)

JSConfigBase = j.tools.configmanager.base_class_configs


class GiteaFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.gitea"        
        self.logger = j.logger.get("j.clients.gitea")
        self._CHILDCLASS = GiteaClient
        JSConfigBase.__init__(self)

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def generate(self):
        """
        generate the client out of the raml specs
        """
        c = j.tools.raml.get(self._path)
        c.client_python_generate()

    def test(self, repo, owner):
        self.generate()
        cl = self.get()
        cl.client.repos.issueListIssues(repo, owner)
        cl.client.repos.issueListLabels(repo, owner)
        cl.client.repos.issueGetMilestones(repo, owner)
        cl.client.user.userListEmails()
