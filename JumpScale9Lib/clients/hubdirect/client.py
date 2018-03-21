from js9 import j

import requests

from .exists_service import ExistsService
from .insert_service import InsertService


TEMPLATE = """
base_uri = "https://direct.hub.gig.tech"
"""


JSConfigBase = j.tools.configmanager.base_class_config


class Client(JSConfigBase):
    def __init__(self, instance, data=None, parent=None, interactive=False):

        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)

        self._session = None
        self._base_url = None
        self.exists = ExistsService(self)
        self.insert = InsertService(self)

    @property
    def base_url(self):
        self._base_url = self.config.data['base_uri']
        return self._base_url

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({"Authorization": j.clients.itsyouonline.get().jwt})
        return self._session

    def is_goraml_class(self, data):
        # check if a data is go-raml generated class
        # we currently only check the existence
        # of as_json method
        op = getattr(data, "as_json", None)
        if callable(op):
            return True
        return False

    def _get_headers(self, headers, content_type):
        if content_type:
            contentheader = {"Content-Type": content_type}
            if headers is None:
                headers = contentheader
            else:
                headers.update(contentheader)
        return headers

    def _handle_data(self, uri, data, headers, params, content_type, method):
        headers = self._get_headers(headers, content_type)
        if self.is_goraml_class(data):
            data = data.as_json()

        if content_type == "multipart/form-data":
            # when content type is multipart/formdata remove the content-type header
            # as requests will set this itself with correct boundary
            headers.pop('Content-Type')
            res = method(uri, files=data, headers=headers, params=params)
        elif data is None:
            res = method(uri, headers=headers, params=params)
        elif type(data) is str:
            res = method(uri, data=data, headers=headers, params=params)
        else:
            res = method(uri, json=data, headers=headers, params=params)
        res.raise_for_status()
        return res

    def post(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.post)

    def put(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.put)

    def patch(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.patch)

    def get(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.get)

    def delete(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self.session.delete)
