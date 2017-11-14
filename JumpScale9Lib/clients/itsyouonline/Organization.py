
from .organizations_service import OrganizationsService
from jose import jwt

class Organization:
    def __init__(self, client):
        self._client = client
        self.global_id = self.global_id_get()

    def global_id_get(self):
        """Get global_id from unverified JWT."""
        claims = jwt.get_unverified_claims(self._client.jwt)
        self.global_id = claims["global_id"]
        return username

    def get_organization_info(self):
        """Get an organization from ItsYou.online."""
        try:
            resp = self._client.organizations.GetOrganization(self, self.global_id)

        except Exception as e:
            print("Error while getting organization: {}".format(_extract_error(e)))

        return resp