from jose import jwt
import logging
from .ApiKey import ApiKeys

class Organizations:
    def __init__(self, user):
        self._user = user
        self._client = user._client

    def list(self):
        """List all organizations that an ItsYou.online user has access too."""

        try:
            resp = self._client.users.GetUserOrganizations(self._user.username)
        except Exception as e:
            logging.exception("Unable to list all user organizations")
            return
        
        user_organizations = list()

        for access_level, global_ids in resp.json().items():
            for global_id in global_ids:
                user_organization = self.get(global_id)
                user_organizations.append(user_organization)
        return user_organizations

    def get(self, global_id):
        """
        Gets an organization with a given global id.

        Args:
            global_id: global id of the organization

        Returns an organization object.
        """
        try:
            resp = self._client.organizations.GetOrganization(global_id)

        except Exception as e:
            logging.exception("Unable to get organization key with global ID %s" % (global_id))
            return

        return Organization(self._client, resp.json())


    def create(self, name):
        """
        Creates a new ItsYou.online organization.

        Args:
            name: name of the organization to create, this name needs to be globally unique

        Returns an organization object.
        """
        data = {
            'globalid': name,
            'owners': [self._user.username] 
        }

        try:
            resp = self._client.organizations.CreateNewOrganization(data)

        except Exception as e:
            logging.exception("Unable to create an new organization key with global ID %s" % (name))
            return

        return Organization(self._client, resp.json())


class Organization:
    def __init__(self, client, model):
        self._client = client
        self.model = model
        self.api_keys = ApiKeys(self)  

    def global_id_get_from_jwt(self):
        """Get global_id from unverified JWT."""
        claims = jwt.get_unverified_claims(self._client.jwt)
        self.global_id = claims["global_id"]
        return self.global_id

    def __repr__(self):
        return "organization: %s" % (self.model["globalid"])

    __str__ = __repr__