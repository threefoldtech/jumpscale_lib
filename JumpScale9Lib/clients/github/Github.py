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

    def get(self, login_or_token, password=None):
        if login_or_token not in self._clients:
            self._clients[login_or_token] = GitHubClient(
                login_or_token, password)
        return self._clients[login_or_token]

    def issue_get(self):
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

    def user_login_get(self, githubObj):
        if githubObj is None:
            return ""
        if githubObj.login not in self.users:
            user = User(self, githubObj=githubObj)
            self.users[githubObj.login] = user
        return self.users[githubObj.login].login

    def user_get(self, login="", githubObj=None):
        if login in self.users:
            return self.users[login]

        if githubObj is not None:
            if githubObj.login not in self.users:
                user = User(self, githubObj=githubObj)
                self.users[githubObj.login] = user
            return self.users[githubObj.login]

    def organizations_get(self):
        """
        gets all organization for an authorized user
        """
        return self.api.get_user().get_orgs()

    def repos_get(self, organizationId=None):
        """
        gets all repos for a user if organizationId=None otherwise it return only repos for this organization

        Args:
            - organizationId (optional): Id for the organization to get repos from

        Raises:
            - RuntimeError if organizationId doesn't exist or the user is not enroled in this organization
        """
        if not organizationId:
            return self.api.get_user().get_repos()
        else:
            orgs = self.api.get_user().get_orgs()
            for org in orgs:
                if org.id == organizationId:
                    return org.get_repos()
            raise RuntimeError("Cannot find Organization with id :%s" % organizationId)

    def repo_get(self, repoName):
        """
        gets a specific repo by name

        Args:
            - repoName: the repo name
        """
        return self.api.get_user().get_repo(repoName)

    def repo_create(self, name, description=NotSet, homepage=NotSet, private=NotSet, has_issues=NotSet, has_wiki=NotSet,
                    has_downloads=NotSet, auto_init=NotSet, gitignore_template=NotSet):
        """
        creates a repo

        Args:
            - name (required): repo name
            - description (optional): repo desription
            - homepage (optional): the home page for the repo
            - private (optional): if true the repo will be created as private repo
            - has_issues (optional): indicates that the repo has issues or no
            - has_wiki (optional): indicates that the repo has wiki or no
            - has_downloads (optional): indicates that the repo has downloads or no
            - auto_init (optional): if true the repo will be automaticly initialized
            - gitignore_template (optional): the gitignore template

        """
        return self.api.get_user().create_repo(name, description=description, homepage=homepage, private=private, has_issues=has_issues,
                    has_wiki=has_wiki, has_downloads=has_downloads, auto_init=auto_init, gitignore_template=gitignore_template)

    def repo_delete(self, repo):
        """
        deletes a repo

        Args:
            - repo (required): a repo to be deleted

        Raises:
            - RuntimeError if repo is not a valid Repository
        """
        if isinstance(repo, github.Repository.Repository):
            repo.delete()
        else:
            raise RuntimeError("invalid Repository")  