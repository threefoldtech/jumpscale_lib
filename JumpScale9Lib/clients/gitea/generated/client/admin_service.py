
from .Organization import Organization
from .PublicKey import PublicKey
from .Repository import Repository
from .User import User
from .api_response import APIResponse
from .unhandled_api_error import UnhandledAPIError
from .unmarshall_error import UnmarshallError


class AdminService:
    def __init__(self, client):
        self.client = client

    def adminDeleteUserPublicKey(self, id, username, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a user's public key
        It is method for DELETE /admin/users/{username}/keys/{id}
        """
        uri = self.client.base_url + "/admin/users/" + username + "/keys/" + id
        return self.client.delete(uri, None, headers, query_params, content_type)

    def adminCreatePublicKey(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Add a public key on behalf of a user
        It is method for POST /admin/users/{username}/keys
        """
        uri = self.client.base_url + "/admin/users/" + username + "/keys"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=PublicKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def adminCreateOrg(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create an organization
        It is method for POST /admin/users/{username}/orgs
        """
        uri = self.client.base_url + "/admin/users/" + username + "/orgs"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Organization(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def adminCreateRepo(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create a repository on behalf a user
        It is method for POST /admin/users/{username}/repos
        """
        uri = self.client.base_url + "/admin/users/" + username + "/repos"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Repository(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def adminDeleteUser(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a user
        It is method for DELETE /admin/users/{username}
        """
        uri = self.client.base_url + "/admin/users/" + username
        return self.client.delete(uri, None, headers, query_params, content_type)

    def adminEditUser(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Edit an existing user
        It is method for PATCH /admin/users/{username}
        """
        uri = self.client.base_url + "/admin/users/" + username
        resp = self.client.patch(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=User(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def adminCreateUser(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Create a user
        It is method for POST /admin/users
        """
        uri = self.client.base_url + "/admin/users"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=User(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)
