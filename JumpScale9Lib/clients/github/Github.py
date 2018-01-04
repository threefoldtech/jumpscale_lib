from js9 import j
from .User import User
from .Issue import Issue

# pygithub is for pip3
import github

JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
login = ""
token_ = ""
password_ = ""
"""


class GitHubFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.github"
        self.__imports__ = "PyGithub"
        self._clients = {}
        JSConfigFactory.__init__(self, GitHubClient)

    # def getRepoClient(self, account, reponame):
    #     return GitHubRepoClient(account, reponame)

    # def getClient(self, login_or_token, password_=None):
    #     if login_or_token not in self._clients:
    #         self._clients[login_or_token] = GitHubClient(
    #             login_or_token, password_)
    #     return self._clients[login_or_token]

    def getIssueClass(self):
        # return Issue
        return Issue


class GitHubClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent)
        self._config = j.tools.configmanager._get_for_obj(
            self, instance=instance, data=data, template=TEMPLATE)
        if not (self.config.data['token_'] or (self.config.data['login'] and self.config.data['password_'])):
            self.config.configure()
        if not (self.config.data['token_'] or (self.config.data['login'] and self.config.data['password_'])):
            raise RuntimeError("Missing Github token_ or login/password_")

        login_or_token = self.config.data['token_'] or self.config.data['login']
        password_ = self.config.data['password_'] if self.config.data['password_'] != "" else None
        self.api = github.Github(login_or_token, password_, per_page=100)
        self.logger = j.logger.get('j.clients.github')
        self.users = {}
        self.repos = {}
        self.milestones = {}

    # def getRepo(self, fullname):
    #     """
    #     fullname e.g. incubaid/myrepo
    #     """
    #     if fullname not in self.repos:
    #         r = self.api.get_repo(fullname)
    #         self.repos[fullname] = r
    #     return self.repos[fullname]

    def getUserLogin(self, githubObj):
        if githubObj is None:
            return ""
        if githubObj.login not in self.users:
            user = User(self, githubObj=githubObj)
            self.users[githubObj.login] = user
        return self.users[githubObj.login].login

    def getUser(self, login="", githubObj=None):
        if login in self.users:
            return self.users[login]

        if githubObj is not None:
            if githubObj.login not in self.users:
                user = User(self, githubObj=githubObj)
                self.users[githubObj.login] = user
            return self.users[githubObj.login]
