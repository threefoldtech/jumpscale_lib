import requests
import urllib

from js9 import j
from JumpScale9Lib.clients.itsyouonline.generated.client import Client

DEFAULT_BASE_URL = "https://itsyou.online/api"

TEMPLATE = """
baseurl = "https://itsyou.online/api"
application_id_ = ""
secret_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config
JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class IYOFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = 'j.clients.itsyouonline'
        self.raml_spec = "https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml"
        JSConfigBaseFactory.__init__(self, IYOClient, single_item=True)

    def install(self):
        j.tools.prefab.local.runtimes.pip.install("python-jose")

    def test(self):
        """
        do:
        js9 'j.clients.itsyouonline.test()'
        """
        from .generated.client.PublicKey import PublicKey
        from requests.exceptions import HTTPError
        client = self.get()
        username = j.tools.myconfig.config.data['login_name']

        # Read all the API keys registered for your user
        print("list all API keys:\n###########")
        for key in client.api.users.ListAPIKeys(username).data:
            print("label: %s" % key.label)
            print("app ID %s" % key.applicationid)

        # Create a new API key
        from requests.exceptions import HTTPError
        try:
            key = client.api.users.AddApiKey({"label": 'test'}, username).data
            print("###########\ncreate new API key: ")
            print("label: %s" % key.label)
            print("app ID %s" % key.applicationid)
        except HTTPError as err:
            # example of how to deal with exceptions
            if err.response.status_code == 409:
                # the key with this label already exists, no need to do anything
                pass
            else:
                raise err

        key_labels = [k.label for k in client.api.users.ListAPIKeys(username).data]
        assert 'test' in key_labels

        print("###########\ndelete api key")
        client.api.users.DeleteAPIkey('test', username)

        key_labels = [k.label for k in client.api.users.ListAPIKeys(username).data]
        assert 'test' not in key_labels

    def jwt_get(self, client_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL):
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


class IYOClient(JSConfigBase, Client):
    def __init__(self, instance, data={}, parent=None):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        Client.__init__(self, base_uri=c['baseurl'])
        self._jwt = None
        self.api.session.headers.update({"Authorization": 'bearer {}'.format(self.jwt)})

    @property
    def jwt(self):
        if self.config.data["application_id_"] == "":
            raise RuntimeError("Please configure your itsyou.online, do this by calling js9 'j.clients.itsyouonline.configure()'")
        if self._jwt == None:
            self._jwt = self._parent.jwt_get(self.config.data["application_id_"], self.config.data["secret_"])
        return self._jwt


    def reset(self):
        self._jwt = None
