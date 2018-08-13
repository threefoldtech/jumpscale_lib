import os
import json
from jumpscale import j

from .GiteaLabels import GiteaLabels
from .GiteaMilestones import GiteaMilestones
from .GiteaIssues import GiteaIssues
from .GiteaRepoPullRequests import GiteaRepoPullRequests
from .GiteaIssueTime import GiteaIssueTime
from .GiteaRepoPublicKeys import GiteaRepoPublicKeys
from .GiteaRepoHooks import GiteaRepoHooks
from .GiteaCommits import GiteaCommits
from .GiteaCollaborators import GiteaCollaborators
from .GiteaBranches import GiteaBranches

JSBASE = j.application.jsbase_get_class()



class GiteaRepo(JSBASE):

    def __init__(
            self,
            client,
            user,
            clone_url=None,
            created_at=None,
            default_branch='master',
            description=None,
            empty=False,
            fork=False,
            forks_count=None,
            full_name=None,
            html_url=None,
            ssh_url=None,
            id=None,
            mirror=None,
            name=None,
            open_issues_count=None,
            owner=None,
            auto_init=True,
            gitignores=None,
            license=None,
            private=True,
            readme=None,
            size=None,
            stars_count=0,
            watchers_count=0,
            permissions=None

    ):
        JSBASE.__init__(self)
        self.user = user
        self.client = client
        self.clone_url = clone_url
        self.description = description
        self.full_name = full_name
        self.id = id
        self.created_at = created_at
        self.default_branch = default_branch
        self.empty = empty
        self.fork = fork
        self.forks_count = forks_count
        self.html_url = html_url
        self.mirror = mirror
        self.name = name
        self.open_issues_count = open_issues_count
        self.owner = owner
        self.auto_init = auto_init
        self.gitignores = gitignores
        self.license=license
        self.private = private
        self.readme = readme
        self.size=size
        self.stars_count=stars_count
        self.watchers_count=watchers_count
        self.permossions=permissions
        self.ssh_url=ssh_url
        self.archive_type = None

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'clone_url',
            'description',
            'full_name',
            'created_at',
            'default_branch',
            'empty',
            'fork',
            'forks_count',
            'html_url',
            'mirror',
            'name',
            'open_issues_count',
            'owner',
            'size',
            'stars_count',
            'watchers_count',
            'permossions',
            'ssh_url'
        ]:

            v = getattr(self, attr)
            if v:
                d[attr] = v
        return d

    def _validate(self, create=False, delete=False, archive=False):
        """
            Validate required attributes are set before doing any operation
        """
        errors = {}
        is_valid = True

        operation = 'create'

        if create:
            if not self.user.is_current and not self.client.users.current.is_admin:
                is_valid = False
                errors['permissions'] = 'Admin permissions required'

            if self.id:
                is_valid = False
                errors['id'] = 'Already existing'
            else:
                if not self.user.username:
                    is_valid = False
                    errors['user'] = {'username':'Missing'}

                if not self.name:
                    is_valid = False
                    errors['name'] = 'Missing'
        elif delete:
            operation = 'delete'
            if not hasattr(self, 'user') or not hasattr(self.user, 'username'):
                return False, 'User is required'
            if not self.name:
                return False, 'Repo name is required'
        elif archive:
            operation = 'archive'
            if not hasattr(self, 'user') or not hasattr(self.user, 'username'):
                return False, 'User is required'
            if not self.name:
                return False, 'Repo name is required'
            if not self.archive_type in ['zip', 'tar.gz']:
                return False, 'Only zip and tar.gz are accepted archive types'

        if is_valid:
            return True, ''

        return False, '{0} Error '.format(operation) + json.dumps(errors)

    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            self.logger.debug(err)
            return is_valid

        try:
            if not self.user.is_current:
                resp = self.user.client.api.admin.adminCreateRepo(data=self.data, username=self.user.username)
            else:
                resp = self.user.client.api.user.createCurrentUserRepo(data=self.data)

            repo = resp.json()
            for k, v in repo.items():
                setattr(self, k, v)

            return True
        except Exception as e:
            if e.response.status_code == 404:
                self.logger.error('not found')
            else:
                self.logger.error(e.response.content)
            return False

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            self.logger.debug(err)
            return is_valid
        try:
            self.user.client.api.repos.repoDelete(repo=self.name, owner=self.user.username)
            self.id = None
            return True
        except Exception as e:
            return False, e.response.content

    def star(self):
        try:

            self.user.client.api.user.userCurrentPutStar(
                data={},
                owner=self.user.username,
                repo=self.name
            )

            return True

        except Exception as e:
            if e.response.status_code == 404:
                self.logger.debug('Repo or owner not found')
            else:
                self.logger.debug(e.response.content)

        return False

    def unstar(self):
        try:
            self.user.client.api.user.userCurrentDeleteStar(
                owner=self.user.username,
                repo=self.name
            )
            return True

        except Exception as e:

            if e.response.status_code == 404:
                self.logger.debug('Repo or owner not found')
            else:
                self.logger.debug(e.response.content)
        return False

    @property
    def is_starred_by_current_user(self):
        try:
            self.user.client.api.user.userCurrentCheckStarring(
                owner=self.user.username,
                repo=self.name
            )

            return True

        except Exception as e:

            if e.response.status_code == 404:
                self.logger.debug('Repo or owner not found')
            else:
                self.logger.debug(e.response.content)
        return False

    def download(self, destination_dir, branch='master', type='zip'):
        self.archive_type = type

        is_valid, err = self._validate(archive=True)

        if not is_valid:
            self.logger.debug(err)
            return is_valid

        try:
            resp = self.user.client.api.repos.repoGetArchive(
                archive=None,
                filepath='%s.%s' % (branch, type),
                repo=self.name, owner=self.user.username
            )

            if not os.path.exists(destination_dir):
                j.sal.fs.createDir(destination_dir)

            path = os.path.join(destination_dir, '%s.%s' % (branch, type))

            with open(path, 'wb') as f:
                f.write(resp.content)
            self.logger.debug('Successfully downloaded %s' % path)
            return True
        except Exception as e:
            if e.response.status_code == 404:
                self.logger.debug('Repo or owner not found')
            else:
                self.logger.debug(e.response.content)
            return False

    def download_file(self, destination_dir, filename, branch='master'):
        """
        get_file('master/knn.py')
        """

        try:
            resp = self.user.client.api.repos.repoGetRawFile(
                filepath='%s/%s' % (branch, filename),
                repo=self.name,
                owner=self.user.username
            )

            if not os.path.exists(destination_dir):
                j.sal.fs.createDir(destination_dir)

            path = os.path.join(destination_dir, filename)

            with open(path, 'wb') as f:
                f.write(resp.content)
            self.logger.debug('Successfully downloaded %s' % path)
            return True
        except Exception as e:
            if e.response.status_code == 404:
                self.logger.debug('Repo or owner not found')
            else:
                self.logger.debug(e.response.content)
            return False

    @property
    def branches(self):
        return GiteaBranches(self.user.client, self, self.user)

    @property
    def collaborators(self):
        return GiteaCollaborators(self.user.client, self, self.user)

    @property
    def commits(self):
        return GiteaCommits(self.user.client, self, self.user)

    @property
    def hooks(self):
        return GiteaRepoHooks(self.user.client, self, self.user)

    @property
    def keys(self):
        return GiteaRepoPublicKeys(self.user, self)

    @property
    def tracked_times(self):
        result = []
        resp = self.user.client.api.repos.repoTrackedTimes(repo=self.name, owner=self.user.username).json()
        for item in resp:
            t = GiteaIssueTime(self.user)
            for k, v in item.items():
                setattr(t, k, v)
            result.append(t)
        return result

    @property
    def pull_requests(self):
        return GiteaRepoPullRequests(self.user.client, self, self.user)

    @property
    def issues(self):
        return GiteaIssues(self.user, self)

    @property
    def milestones(self):
        return GiteaMilestones(self.user.client, self, self.user)

    @property
    def labels(self):
        return GiteaLabels(self.user.client, self, self.user)



    def __str__(self):
        return '\n<Repo>\n%s' % json.dumps(self.data, indent=4)

    __repr__ = __str__