from .users_service import UsersService
from .PublicKey import PublicKeys
from jose import jwt
import logging

class User:
    def __init__(self, client):
        self._client = client
        self.username = self.username_get()
        self.model = self.model_get()
        self.public_keys = PublicKeys(self)

    def username_get(self):
        """Get username from unverified JWT."""
        claims = jwt.get_unverified_claims(self._client.jwt)
        self.username = claims["username"]
        return self.username

    def model_get(self):
        """get all all user info from ItsYou.online"""
        try:
            resp = self._client.users.GetUser(self.username)

        except Exception as e:
            logging.exception("Error while getting organization")
            return
        
        return resp.json()

    def __repr__(self):
        return "user: %s" % (self.model["username"])

    __str__ = __repr__