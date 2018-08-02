import json
from jumpscale import j

from .GiteaTeams import GiteaTeams
from .GiteaOrgMembers import GiteaOrgMembers
from .GiteaOrgRepos import GiteaOrgRepos
from .GiteaOrgHooks import GiteaOrgHooks

JSBASE = j.application.jsbase_get_class()


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
        return GiteaOrgRepos()

    @property
    def members(self):
        return GiteaOrgMembers(self.user.client, self)

    @property
    def teams(self):
        return  GiteaTeams(self.user.client, self)

    def __repr__ (self):
        return '\n<Organization>\n{0}'.format(
            json.dumps(self.data, indent=4)
        )

    __str__ = __repr__
