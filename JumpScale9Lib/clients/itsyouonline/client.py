import requests
from .users_service import UsersService
from .organizations_service import OrganizationsService 

DEFAULT_URL = "https://itsyou.online/api"

class Client:
    def __init__(self, jwt):
        self.jwt = jwt
        self.base_url = DEFAULT_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"Authorization": 'bearer {}'.format(jwt)})
        self.users = UsersService(self)
        self.organizations = OrganizationsService(self)

    def get_jwt(id, secret):
        """
        Get a a JSON Web token for an ItsYou.online organization or user.

        Args:
            id: client ID of the API access key of the ItsYou.online organization, or application ID of the API access key of the ItsYou.online user
            secret: secret of the API access key of the ItsYou.online organization or user
        """
        params = {
            'grant_type': 'client_credentials',
            'client_id': id,
            'client_secret': secret,
            'response_type': 'id_token'
        }
        url = 'https://itsyou.online/v1/oauth/access_token'
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt = resp.content.decode('utf8')
        return jwt


    def get_headers(self, headers, content_type):
        if content_type:
            contentheader = {"Content-Type": content_type}
            if headers is None:
                headers = contentheader
            else:
                headers.update(contentheader)
        return headers

    def get(self, uri, data, headers, params, content_type):
        headers = self.get_headers(headers, content_type)
       
        res = self.session.get(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def post(self, uri, data, headers, params, content_type):
        if isinstance(data, str):
            return self.session.post(uri, data=data, headers=headers, params=params)
        else:
            return self.session.post(uri, json=data, headers=headers, params=params)

    def delete(self, uri, data, headers, params, content_type):
        headers = self.get_headers(headers, content_type)
        res = self.session.delete(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def put(self, uri, data, headers, params, content_type):
        if isinstance(data, str):
            return self.session.put(uri, data=data, headers=headers, params=params)
        else:
            self.session.put(uri, json=data, headers=headers, params=params)

    def patch(self, uri, data, headers, params, content_type):
        if isinstance(data, str):
            return self.session.patch(uri, data=data, headers=headers, params=params)
        else:
            return self.session.patch(uri, json=data, headers=headers, params=params)
