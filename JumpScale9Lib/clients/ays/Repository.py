from js9 import j
from requests.exceptions import HTTPError
from .Blueprint import Blueprints
from .Service import Services
from .Run import Runs

def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp

class Repositories:
    def __init__(self, client):
        self._client = client
        self._api = client._ayscl.api.ays

    def list(self):
        ays_repositories = self._api.listRepositories().json()
        repositories = list()
        for repository in ays_repositories:
            repositories.append(Repository(self._client, repository))
        return repositories

    def get(self, name):
        for repository in self.list():
            if repository.model.get('name') == name:
                return repository
        raise ValueError("Could not find repository with name {}".format(name))

    def create(self, name, git):
        data = j.data.serializer.json.dumps({'name': name, 'git_url': git})
        self._api.createRepository(data)
        return self.get(name)


class Repository:
    def __init__(self, client, model):
        self._client = client
        self._api = client._ayscl.api.ays
        self.model = model
        self.blueprints = Blueprints(self)
        self.services = Services(self)
        self.runs = Runs(self)

    def destroy(self):
        """
        All services and runs will be deleted, blueprints are kept
        Make sure to do a commit before you do a distroy, this will give you a chance to roll back.
        """
        try:
            resp = self._api.destroyRepository(data=None, repository=self.model["name"])
        except Exception as e:
            print("Error while destroying repository: {}".format(_extract_error(e)))

    def delete(self):
        """
        Delete everything, including the repository itself, all services, runs and blueprints will be lost.
        Make sure to do a commit before you do a delete, this will give you a chance to roll back.
        """
        try:
            resp = self._api.deleteRepository(repository=self.model["name"])
        except Exception as e:
            print("Error while deleting repository: {}".format(_extract_error(e)))

    def __repr__(self):
        return "repository: %s" % (self.model["name"])

    __str__ = __repr__
