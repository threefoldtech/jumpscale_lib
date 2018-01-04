
from js9 import j
import os
import sys

from .GiteaClient import GiteaClient
from pprint import pprint as print
# https://docs.grid.tf/api/swagger example api source


# TODO: (phase 2): export/import a full repo (with issues, milestones & labels) (per repo)

JSConfigBase = j.tools.configmanager.base_class_configs


class GiteaFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.gitea"
        self.logger = j.logger.get("gitea")
        JSConfigBase.__init__(self, GiteaClient)

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def generate(self):
        """
        generate the client out of the raml specs
        """
        c = j.tools.raml.get(self._path)
        c.client_python_generate()

    def labels_milestones_set(self, orgname="*", reponame="*", instance="main", remove_old=False):
        """
        * means all in the selection

        @PARAM remove_old if True will select labels/milestones which are old & need to be removed

        """
        self.logger.info("labels_milestones_set:%s:%s" % (orgname, reponame))
        cl = self.get(instance=instance)
        if orgname == "*":
            for orgname0 in cl.orgs_currentuser_list():
                # print(cl.orgs_currentuser_list())
                # print("orgname0:%s"%orgname0)
                self.labels_milestones_set(orgname=orgname0, reponame=reponame, instance=instance, remove_old=remove_old)
            return

        org = cl.org_get(orgname)

        if reponame == "*":
            for reponame0 in org.repos_list():
                # print(org.repos_list())
                # print("reponame0:%s"%reponame0)
                self.labels_milestones_set(orgname=orgname, reponame=reponame0, instance=instance, remove_old=remove_old)
            return

        repo = org.repo_get(reponame)
        repo.labels_add(remove_old=remove_old)
        repo.milestones_add(remove_old=remove_old)

    def test(self):
        """
        js9 'j.clients.gitea.test()'
        """
        # self.generate()
        cl = self.get()

        print(cl.orgs_currentuser_list())

        names = [item for item in cl.orgs_currentuser_list().keys()]
        names.sort()
        if "threefold" in names:
            name = "threefold"
        else:
            name = names[0]

        org = cl.org_get(name)

        # CAREFULL WILL GO OVER ALL MILESTONES
        # org.labels_milestones_add(remove_old=False)

        print(org.repos_list())

        repoName = [item for item in org.repos_list().keys()][0]  # first reponame

        repo = org.repo_get(repoName)

        # repo.labels_add()
        # repo.milestones_add(remove_old=False)

        print(repo.issues_get())
