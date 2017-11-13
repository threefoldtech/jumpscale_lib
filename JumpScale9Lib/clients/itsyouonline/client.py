import requests

DEFAULT_URL = "https://itsyou.online/api"

class Client:
    def __init__(self, jwt):
        self.jwt = jwt
        self._base_url = DEFAULT_URL
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._session.headers.update({"Authorization": jwt})

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

    def set_auth_header(self, val):
        """Set authorization header value."""
        self._session.headers.update({"Authorization": val})

    def post(self, uri, data, headers, params):
        if isinstance(data, str):
            return self._session.post(uri, data=data, headers=headers, params=params)
        else:
            return self._session.post(uri, json=data, headers=headers, params=params)

    def put(self, uri, data, headers, params):
        if isinstance(data, str):
            return self._session.put(uri, data=data, headers=headers, params=params)
        else:
            self._session.put(uri, json=data, headers=headers, params=params)

    def patch(self, uri, data, headers, params):
        if isinstance(data, str):
            return self._session.patch(uri, data=data, headers=headers, params=params)
        else:
            return self._session.patch(uri, json=data, headers=headers, params=params)
