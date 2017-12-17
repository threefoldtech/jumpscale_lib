


class UserService:
    def __init__(self, client):
        self.client = client


    def userDeleteEmail(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for DELETE /user/emails
        """
        uri = self.client.base_url + "/user/emails"
        return self.client.delete(uri, data, headers, query_params, content_type)

    def userListEmails(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/emails
        """
        uri = self.client.base_url + "/user/emails"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userAddEmail(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for POST /user/emails
        """
        uri = self.client.base_url + "/user/emails"
        return self.client.post(uri, data, headers, query_params, content_type)

    def userCurrentListFollowers(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/followers
        """
        uri = self.client.base_url + "/user/followers"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentCheckFollowing(self, followee, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/following/{followee}
        """
        uri = self.client.base_url + "/user/following/"+followee
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentDeleteFollow(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for DELETE /user/following/{username}
        """
        uri = self.client.base_url + "/user/following/"+username
        return self.client.delete(uri, None, headers, query_params, content_type)

    def userCurrentPutFollow(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for PUT /user/following/{username}
        """
        uri = self.client.base_url + "/user/following/"+username
        return self.client.put(uri, data, headers, query_params, content_type)

    def userCurrentListFollowing(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/following
        """
        uri = self.client.base_url + "/user/following"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentDeleteGPGKey(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for DELETE /user/gpg_keys/{id}
        """
        uri = self.client.base_url + "/user/gpg_keys/"+id
        return self.client.delete(uri, None, headers, query_params, content_type)

    def userCurrentGetGPGKey(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/gpg_keys/{id}
        """
        uri = self.client.base_url + "/user/gpg_keys/"+id
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentListGPGKeys(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/gpg_keys
        """
        uri = self.client.base_url + "/user/gpg_keys"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentPostGPGKey(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for POST /user/gpg_keys
        """
        uri = self.client.base_url + "/user/gpg_keys"
        return self.client.post(uri, data, headers, query_params, content_type)

    def userCurrentDeleteKey(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for DELETE /user/keys/{id}
        """
        uri = self.client.base_url + "/user/keys/"+id
        return self.client.delete(uri, None, headers, query_params, content_type)

    def userCurrentGetKey(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/keys/{id}
        """
        uri = self.client.base_url + "/user/keys/"+id
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentListKeys(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/keys
        """
        uri = self.client.base_url + "/user/keys"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentPostKey(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for POST /user/keys
        """
        uri = self.client.base_url + "/user/keys"
        return self.client.post(uri, data, headers, query_params, content_type)

    def orgListCurrentUserOrgs(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/orgs
        """
        uri = self.client.base_url + "/user/orgs"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentListRepos(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/repos
        """
        uri = self.client.base_url + "/user/repos"
        return self.client.get(uri, None, headers, query_params, content_type)

    def createCurrentUserRepo(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for POST /user/repos
        """
        uri = self.client.base_url + "/user/repos"
        return self.client.post(uri, data, headers, query_params, content_type)

    def userCurrentDeleteStar(self, repo, owner, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for DELETE /user/starred/{owner}/{repo}
        """
        uri = self.client.base_url + "/user/starred/"+owner+"/"+repo
        return self.client.delete(uri, None, headers, query_params, content_type)

    def userCurrentCheckStarring(self, repo, owner, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/starred/{owner}/{repo}
        """
        uri = self.client.base_url + "/user/starred/"+owner+"/"+repo
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentPutStar(self, data, repo, owner, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for PUT /user/starred/{owner}/{repo}
        """
        uri = self.client.base_url + "/user/starred/"+owner+"/"+repo
        return self.client.put(uri, data, headers, query_params, content_type)

    def userCurrentListStarred(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/starred
        """
        uri = self.client.base_url + "/user/starred"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentListSubscriptions(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/subscriptions
        """
        uri = self.client.base_url + "/user/subscriptions"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCurrentTrackedTimes(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/times
        """
        uri = self.client.base_url + "/user/times"
        return self.client.get(uri, None, headers, query_params, content_type)

    def orgListUserOrgs(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user/{username}/orgs
        """
        uri = self.client.base_url + "/user/"+username+"/orgs"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userGetCurrent(self, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /user
        """
        uri = self.client.base_url + "/user"
        return self.client.get(uri, None, headers, query_params, content_type)
