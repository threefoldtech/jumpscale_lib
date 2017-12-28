import requests

from .admin_service import AdminService
from .markdown_service import MarkdownService
from .org_service import OrgService
from .orgs_service import OrgsService
from .repos_service import ReposService
from .repositories_service import RepositoriesService
from .teams_service import TeamsService
from .user_service import UserService
from .users_service import UsersService
from .version_service import VersionService


class Client:
    def __init__(self, base_uri="http://example.com/api/v1"):
        self.base_url = base_uri
        self.session = requests.Session()
        self.admin = AdminService(self)
        self.markdown = MarkdownService(self)
        self.org = OrgService(self)
        self.orgs = OrgsService(self)
        self.repos = ReposService(self)
        self.repositories = RepositoriesService(self)
        self.teams = TeamsService(self)
        self.user = UserService(self)
        self.users = UsersService(self)
        self.version = VersionService(self)

    def is_goraml_class(self, data):
        # check if a data is go-raml generated class
        # we currently only check the existence
        # of as_json method
        op = getattr(data, "as_json", None)
        if callable(op):
            return True
        return False

    def set_auth_header(self, val):
        ''' set authorization header value'''
        self.session.headers.update({"Authorization": val})

    def _get_headers(self, headers, content_type):
        if content_type:
            contentheader = {"Content-Type": content_type}
            if headers is None:
                headers = contentheader
            else:
                headers.update(contentheader)
        return headers

    def _handle_data(self, uri, data, headers, params, content_type, method):
        headers = self._get_headers(headers, content_type)
        if self.is_goraml_class(data):
            data = data.as_json()

        if content_type == "multipart/form-data":
            # when content type is multipart/formdata remove the content-type header
            # as requests will set this itself with correct boundary
            headers.pop('Content-Type')
            res = method(uri, files=data, headers=headers, params=params)
        elif data is None:
            res = method(uri, headers=headers, params=params)
        elif isinstance(data, str):
            res = method(uri, data=data, headers=headers, params=params)
        else:
            res = method(uri, json=data, headers=headers, params=params)
        res.raise_for_status()
        return res

    def post(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.post)

    def put(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.put)

    def patch(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.patch)

    def get(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.get)

    def delete(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.delete)
