

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
        return self.client.post(uri, data, headers, query_params, content_type)

    def adminCreateOrg(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create an organization
        It is method for POST /admin/users/{username}/orgs
        """
        uri = self.client.base_url + "/admin/users/" + username + "/orgs"
        return self.client.post(uri, data, headers, query_params, content_type)

    def adminCreateRepo(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create a repository on behalf a user
        It is method for POST /admin/users/{username}/repos
        """
        uri = self.client.base_url + "/admin/users/" + username + "/repos"
        return self.client.post(uri, data, headers, query_params, content_type)

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
        return self.client.patch(uri, data, headers, query_params, content_type)

    def adminCreateUser(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Create a user
        It is method for POST /admin/users
        """
        uri = self.client.base_url + "/admin/users"
        return self.client.post(uri, data, headers, query_params, content_type)
