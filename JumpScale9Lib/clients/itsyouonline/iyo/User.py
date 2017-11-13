from .users_service import UsersService
from jose import jwt

class User:
    def __init__(self, client):
        self._client = client
        self._users_cl = UsersService(client)
        self.username = username_get()

    def username_get(self):
        """Get username from unverified JWT."""
        claims = jose.jwt.get_unverified_claims(self._client.jwt)
        username = claims["username"]
        return username

    def user_get(self):
        """get all all user info from ItsYou.online"""

        try:
            resp = self._users_cl.GetUser(self.username)

        except Exception as e:
            print("Error while getting organization: {}".format(_extract_error(e)))

        return resp

