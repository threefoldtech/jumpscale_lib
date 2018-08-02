
from jumpscale import j
import os
import sys

from .GiteaClient import GiteaClient
from pprint import pprint as print
# https://docs.grid.tf/api/swagger example api source


# TODO: (phase 2): export/import a full repo (with issues, milestones & labels) (per repo)

JSConfigBase = j.tools.configmanager.base_class_configs
JSBASE = j.application.jsbase_get_class()


class GiteaFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.gitea"
        JSConfigBase.__init__(self, GiteaClient)

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def get_by_params(self,instance,url,gitea_token, admins):
        data={}
        data["url"]=instance
        data["gitea_token_"]=gitea_token
        data["admins"]=[admin.stripr() for admin in admins.split(',')]
        self.get(instance=instance,data=data)

    def generate(self):
        """
        generate the client out of the raml specs

        get your token from https://docs.grid.tf/user/settings/applications

        """
        c = j.tools.raml.get(self._path)
        c.client_python_generate()

    def test(self):
        """
        js9 'j.clients.gitea.test()'
        """
        # self.generate()
        cl = self.get()
        cl.cache.reset()

        # Test start
        j.logger.logger.info('\n\n\n### Test Start\n\n\n')

        # Print API version
        j.logger.logger.info(cl.version)

        # Admin

        admin = cl.admin
        admin.test()

        j.logger.logger.info('\n\n\n### Test End\n\n\n')
