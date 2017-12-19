import pytest
from js9 import j

from .Github import *

NotSet = github.GithubObject.NotSet

@pytest.fixture(autouse=True)
def no_org_object(monkeypatch):
    """
    mocking organization object
    """
    class Org:
        def __init__(self, id):
            self.id = id
        def get_repos(self):
            return True
    monkeypatch.setattr(github.Organization, "Organization", Org)

@pytest.fixture(autouse=True)
def no_user_get_repo(monkeypatch):
    """
    mocking get_repo method
    """
    def get_repo(self, reponame):
        return True
    monkeypatch.setattr(github.AuthenticatedUser.AuthenticatedUser, 'get_repo', get_repo)

@pytest.fixture(autouse=True)
def no_user_get_orgs(monkeypatch):
    """
    mocking get_orgs method
    """
    def get_orgs(self):
        return [github.Organization.Organization("id")]
    monkeypatch.setattr(github.AuthenticatedUser.AuthenticatedUser, 'get_orgs', get_orgs)

@pytest.fixture(autouse=True)
def no_user_get_repos(monkeypatch):
    """
    mocking get_repos method
    """
    def get_repos(self, organizationId=None):
        if organizationId:
            return False
        else:
            return True
    monkeypatch.setattr(github.AuthenticatedUser.AuthenticatedUser, 'get_repos', get_repos)

@pytest.fixture(autouse=True)
def no_user_create_repo(monkeypatch):
    """
    mocking create_repo method
    """
    def create_repo(self, name, description=NotSet, homepage=NotSet, private=NotSet, has_issues=NotSet, has_wiki=NotSet,
                    has_downloads=NotSet, auto_init=NotSet, gitignore_template=NotSet):
        return True
    monkeypatch.setattr(github.AuthenticatedUser.AuthenticatedUser, 'create_repo', create_repo)


@pytest.mark.github_client
def test_repo_get():
    """
    test repo_get method
    """
    assert j.clients.github.get("token").repo_get("test")

@pytest.mark.github_client
def test_organizations_get():
    """
    test organizations_get method
    """
    assert j.clients.github.get("token").organizations_get()[0].id == "id"

@pytest.mark.github_client
def test_repos_get_without_organization():
    """
    test repos_get method without organizationId
    """
    assert j.clients.github.get("token").repos_get()

@pytest.mark.github_client
def test_repos_get_with_organization():
    """
    test repos_get method for organizationId
    """
    assert j.clients.github.get("token").repos_get(organizationId="id")

@pytest.mark.github_client
def test_repos_create():
    """
    test repos_create method for organizationId
    """
    assert j.clients.github.get("token").repo_create(name="repo")

@pytest.mark.github_client
def test_repo_delete():
    """
    test repo_delete method for organizationId
    """
    try:
        j.clients.github.get("token").repo_delete("invalid")
        assert False
    except RuntimeError:
        assert True

