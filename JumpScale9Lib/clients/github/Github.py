from js9 import j
from .User import User
from .Issue import Issue


try:
    import github
except BaseException:
    cmd = "pip3 install pygithub"
    j.sal.process.execute(cmd)
    import github


class GitHubFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.github"
        self.__imports__ = "PyGithub"
        self._clients = {}

    # def getRepoClient(self, account, reponame):
    #     return GitHubRepoClient(account, reponame)

    def getClient(self, login_or_token, password=None):
        if login_or_token not in self._clients:
            self._clients[login_or_token] = GitHubClient(login_or_token, password)
        return self._clients[login_or_token]

    def getIssueClass(self):
        # return Issue
        return Issue


class GitHubClient:

    def __init__(self, login_or_token, password=None):
        self.api = github.Github(login_or_token, password, per_page=100)
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
