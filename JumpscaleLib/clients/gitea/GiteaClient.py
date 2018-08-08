import json

from jumpscale import j

from .GiteaReposForClient import GiteaReposForClient

from .GiteaOrgs import GiteaOrgs
from .GiteaMarkdowns import GiteaMarkdowns
from .GiteaUsers import GiteaUsers
from JumpscaleLib.clients.gitea.client import Client


TEMPLATE = """
url = ""
gitea_token_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config
JSBASE = j.application.jsbase_get_class()


class GiteaClient(JSConfigBase):
    def __init__(
            self,
            instance,
            data={},
            parent=None,
            interactive=False
    ):

        JSConfigBase.__init__(
            self,
            instance=instance,
            data=data,
            parent=parent,
            template=TEMPLATE,
            interactive=interactive
        )

        self._api = None
        self.version = self.api.version.getVersion().json()['version']
        self.markdowns = GiteaMarkdowns(self)
        self.users = GiteaUsers(self)
        self.organizations = GiteaOrgs(client=self, user=self.users.current)
        self.repos = GiteaReposForClient(client=self, user=self.users.current)

    def config_check(self):
        """
        check the configuration if not what you want the class will barf & show you where it went wrong
        """
        if self.config.data["url"] == "" or self.config.data["gitea_token_"] == "":
            return "url and gitea_token_ are not properly configured, cannot be empty"

        base_uri = self.config.data["url"]
        if "/api" not in base_uri:
            self.config.data_set("url", "%s/api/v1" % base_uri)
            self.config.save()

        # TODO:*1 need to do more checks that url is properly formated

    @property
    def api(self):
        if not self._api:
            self._api = Client(base_uri=self.config.data["url"])
            self._api.security_schemes.passthrough_client_token.set_authorization_header(
                'token {}'.format(self.config.data["gitea_token_"]))
        return self._api

    def test(self):
        self.markdowns.test()

    def __repr__(self):
        return '<Gitea Client: v={0} user={1} admin={2}>'.format(
            self.version,
            self.users.current.data['username'],
            self.users.current.is_admin
        )

    __str__ = __repr__