
from js9 import j
import os
import sys

from .GiteaClient import GiteaClient
from pprint import pprint as print
#https://docs.grid.tf/api/swagger example api source


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
        """
        js9 'j.clients.gitea.test()'
        """
        # self.generate()
        cl = self.get()

        print(cl.client.orgs.orgListMembers("threefold").data)
        from IPython import embed;embed(colors='Linux')

        cl.client.repos.issueListIssues(repo, owner)
        cl.client.repos.issueListLabels(repo, owner)
        cl.client.repos.issueGetMilestones(repo, owner)
        cl.client.user.userListEmails()
