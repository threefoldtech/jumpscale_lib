import requests
import urllib

from js9 import j
from JumpScale9Lib.clients.itsyouonline.generated.client import Client

SecretConfigBase = j.tools.secretconfig.base_class_secret


DEFAULT_BASE_URL = "https://itsyou.online/api"

TEMPLATE = """
baseurl = "https://itsyou.online/api"
application_id_ = ""
secret_ = ""
"""


class IYOFactory(SecretConfigBase):

    def __init__(self):
        self.__jslocation__ = 'j.clients.itsyouonline'
        self._jwt = None
        self.raml_spec = "https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml"

        # configure sercret config
        self.instance = "main"
        self._TEMPLATE = TEMPLATE

    def get(self):
        """
        Get an ItsYouOnline REST API client
        """
        client = Client()
        client.api.session.headers.update({"Authorization": 'bearer {}'.format(self.jwt)})
        return client

    @property
    def jwt(self):
        if self._jwt == None:
            self._jwt = self.get_jwt(self.config.data["application_id_"], self.config.data["secret_"])
        return self._jwt

    def get_jwt(self, client_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL):
        """
        Get a a JSON Web token for an ItsYou.online organization or user.

        Args:
            client_id: global ID of the ItsYou.online organization or application ID of the API access key of the ItsYou.online user
            secret: secret of the API access key of the ItsYou.online organization or user
            validity: time in seconds after which the JWT will become invalid; defaults to 3600
            refreshable (True/False): If true the JWT can be refreshed; defaults to False
            scope: defaults to None
            base_url: base url of the ItsYou.online service; defaults to https://itsyou.online
        """
        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': secret,
            'response_type': 'id_token'
        }

        if validity:
            params["validity"] = validity

        if refreshable:
            params["scope"] = 'offline_access'

        if scope:
            if refreshable:
                params["scope"] = params["scope"] + "," + scope
            else:
                params["scope"] = scope

        url = urllib.parse.urljoin(base_url, '/v1/oauth/access_token')
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt = resp.content.decode('utf8')
        return jwt
