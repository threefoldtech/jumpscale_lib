import requests
from js9 import j
from .ays_service import AysService 
from .Repository import Repositories

class Client:
    def __init__(self, base_uri=BASE_URI, jwt=None):
        self._base_url = base_uri
        self._session = requests.Session() 
        self._session.headers.update({"Content-Type": "application/json"})
        self._ayscl = AysService(self)
        self.repositories = Repositories(self)
        if jwt:
            self._set_auth_header('Bearer {}'.format(jwt))

    def _set_auth_header(self, val):
        ''' set authorization header value'''
        self._session.headers.update({"Authorization": val})

    def _get_headers(self, headers, content_type):
        if content_type:
            contentheader = {"Content-Type": content_type}
            if headers is None:
                headers = contentheader
            else:
                headers.update(contentheader)
        return headers

    def _get(self, uri, headers, params, content_type):
        headers = self._get_headers(headers, content_type)
        res = self._session.get(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def _delete(self, uri, headers, params, content_type):
        headers = self._get_headers(headers, content_type)
        res = self._session.delete(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def _post(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self._session.post)

    def _put(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self._session.put)