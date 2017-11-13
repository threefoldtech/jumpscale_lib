from .User import User
from .Organization import Organization
from .client import Client

DEFAULT_URL = "https://itsyou.online"

class ClientFactory:

    def __init__(self):
        self.__jslocation__ = 'j.clients.itsyouonline'

    def get_user(self, application_id, secret, url=DEFAULT_URL):
        """
        Get a client object for an ItsYou.online user.

        Args:
            application_id: Application ID of the API access key of the ItsYou.online user
            secret: secret of the API access key of the ItsYou.online user
            url: url of the ItsYou.online service; defaults to https://itsyou.online
        """
        jwt = Client.get_jwt(application_id, secret)
        return get_user_with_jwt(jwt)

    def get_organization(self, global_id, secret, url=DEFAULT_URL):
        """
        Get a client object for an ItsYou.online organization.

        Args:
            global_id: global ID (client ID) of the API access key of the ItsYou.online organization
            secret: secret of the API access key of the ItsYou.online organization
            url: url of the ItsYou.online service; defaults to https://itsyou.online
        """
        jwt = Client.get_jwt(global_id, secret)
        return get_organization_with_jwt(jwt)

    def get_user_with_jwt(self, jwt):
        """
        Get a client object for an ItsYou.online user.

        Args:
            jwt: JSON Web token created for an ItsYou.online user
        """
        client = Client(jwt)
        return User(client) 

    def get_organization_with_jwt(self, jwt):
        """
        Get a client object for an ItsYou.online organization.

        Args:
            jwt: JSON Web token created for an ItsYou.online organization
        """
        client = Client(jwt)
        return Organization(client)