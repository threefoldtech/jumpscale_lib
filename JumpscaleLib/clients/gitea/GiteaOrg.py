import json
from jumpscale import j

from .GiteaTeams import GiteaTeams
from .GiteaOrgMembers import GiteaOrgMembers
from .GiteaOrgRepos import GiteaOrgRepos
from .GiteaOrgHooks import GiteaOrgHooks
from .GiteaRepo import GiteaRepo
JSBASE = j.application.jsbase_get_class()

default_labels = [
    {'color': '#e11d21', 'name': 'priority_critical'},
    {'color': '#f6c6c7', 'name': 'priority_major'},
    {'color': '#f6c6c7', 'name': 'priority_minor'},
    {'color': '#d4c5f9', 'name': 'process_duplicate'},
    {'color': '#d4c5f9', 'name': 'process_wontfix'},
    {'color': '#bfe5bf', 'name': 'state_inprogress'},
    {'color': '#bfe5bf', 'name': 'state_question'},
    {'color': '#bfe5bf', 'name': 'state_verification'},
    {'color': '#fef2c0', 'name': 'type_bug'},
    {'color': '#fef2c0', 'name': 'type_task'},
    {'color': '#fef2c0', 'name': 'type_story'},
    {'color': '#fef2c0', 'name': 'type_feature'},
    {'color': '#fef2c0', 'name': 'type_question'}
]
class GiteaOrg(JSBASE):

    def __init__(
            self,
            client,
            user,
            avatar_url=None,
            description=None,
            full_name=None,
            id=None,
            location=None,
            username=None,
            website=None
    ):
        JSBASE.__init__(self)
        self.client = client
        self.user = user
        self.avatar_url = avatar_url
        self.description = description
        self.full_name = full_name
        self.id = id
        self.location = location
        self.username = username
        self.website = website

    def labels_default_get(self):
        return default_labels

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'avatar_url',
            'description',
            'full_name',
            'location',
            'username',
            'website',
        ]:

            v = getattr(self, attr)
            d[attr] = v
        return d

    def _validate(self, create=False, update=False, delete=False):
        errors = {}
        is_valid = True

        operation = 'create'
        if create:
            if not self.user.is_current:
                is_valid = False
                errors['permissions'] = 'Admin permissions required'

            if self.id:
                is_valid = False
                errors['id'] = 'Already existing'
            else:
                if not self.user.username:
                    is_valid = False
                    errors['user'] = {'username':'Missing'}

                if not self.full_name:
                    is_valid = False
                    errors['full_name'] = 'Missing'

                if not self.username:
                    is_valid = False
                    errors['username'] = 'Missing'
        elif update:
            operation = 'update'
            if not self.user.is_member_of_org(self.username):
                is_valid = False
                errors['permissions'] = 'user is not member of the organization'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'
            if not self.username:
                is_valid = False
                errors['id'] = 'Missing'

        elif delete:
            operation = 'delete'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'
            if not self.username:
                is_valid = False
                errors['id'] = 'Missing'
            if not self.user.is_current and not self.client.users.current.is_admin:
                is_valid = False
                errors['permissions'] = 'Admin permissions required'

        if is_valid:
            return True, ''

        return False, '{0} Error '.format(operation) + json.dumps(errors)

    @property
    def hooks(self):
        return GiteaOrgHooks(self.user.client, self)

    @property
    def repos(self):
        return GiteaOrgRepos(self)

    @property
    def members(self):
        return GiteaOrgMembers(self.user.client, self)

    @property
    def teams(self):
        return  GiteaTeams(self.user.client, self)

    def _repos_get(self, refresh=False):
        def do():
            res = {}
            repos = self.client.api.orgs.orgListRepos(self.username)
            repos_json = json.loads(repos.text)
            for item in repos_json:
                res[item['name']] = item
            return res
        return self.cache.get("orgs", method=do, refresh=refresh, expire=60)

    def repos_list(self, refresh=False):
        """list repos in that organization
         :param refresh: if true will not use value in cache, defaults to False
        :param refresh: bool, optional
        :return: key-value of repo name and id
        :rtype: dict
        """
        res = {}
        for name, item in self._repos_get(refresh=refresh).items():
            res[name] = item['id']
        return res

    def repo_get(self, name):
        """returns a gitea repo object
         :param name: name of the repo
        :type name: str
        :raises RuntimeError: if soecified name not in org's repos
        :return: gitea object
        :rtype: object
        """
        self.logger.info("repo:get:%s" % name)
        if name not in self._repos_get().keys():
            raise RuntimeError("cannot find repo with name:%s in %s" % (name, self))
        data = self._repos_get()[name]
        return GiteaRepo(self, name, data)

    def repo_new(self, name):
        """create a new repo if it doesn't exist
         :param name: name of the new repo
        :type name: str
        :return: response data which includes repo info and repo object from generated client
        :rtype: tuple
        """
        self.logger.info("repo:new:%s" % name)
        if name in self._repos_get().keys():
            self.logger.debug("no need to create repo on gitea, exists:%s"%name)
            return self._repos_get()[name]
        else:
            data = {'name': name}
            return self.client.api.org.createOrgRepo(data, org=self.username)

    def __repr__ (self):
        return '\n<Organization>\n{0}'.format(
            json.dumps(self.data, indent=4)
        )

    __str__ = __repr__
