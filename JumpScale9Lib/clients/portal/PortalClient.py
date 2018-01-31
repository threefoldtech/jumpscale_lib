import requests
import os
import json
from js9 import j

TEMPLATE = """
ip = ""
port = 8200
iyoinstance = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class ApiError(Exception):
    def __init__(self, response):
        msg = '%s %s' % (response.status_code, response.reason)
        try:
            message = response.json()
        except BaseException:
            message = response.content
        if isinstance(message, (str, bytes)):
            msg += '\n%s' % message
        elif isinstance(message, dict) and 'errormessage' in message:
            msg += '\n%s' % message['errormessage']

        super(ApiError, self).__init__(msg)
        self._response = response

    @property
    def response(self):
        return self._response


class BaseResource:
    def __init__(self, session, url):
        self._session = session
        self._url = url
        self._method = 'POST'

    def __getattr__(self, item):
        url = os.path.join(self._url, item)
        resource = BaseResource(self._session, url)
        setattr(self, item, resource)
        return resource

    def __call__(self, **kwargs):
        response = self._session.request(self._method, self._url, kwargs)

        if not response.ok:
            raise ApiError(response)

        if response.headers.get('content-type', 'text/html') == 'application/json':
            return response.json()

        return response.content


class Resource(BaseResource):
    def __init__(self, ip, port, path):
        session = requests.Session()

        scheme = "http" if port != 443 else "https"
        url = "%s://%s:%s/%s" % (scheme, ip, port, path.lstrip('/'))

        super(Resource, self).__init__(session, url)

    def load_swagger(self, file=None, group=None):
        if file:
            with open(file) as fd:
                swagger = json.load(fd)
        else:
            swagger = self.system.docgenerator.prepareCatalog(group=group)

        for methodpath, methodspec in swagger['paths'].items():
            api = self
            for path in methodpath.split('/')[1:]:
                api = getattr(api, path)
            method = 'post'
            if 'post' not in methodspec and methodspec:
                method = list(methodspec.keys())[0]
            api._method = method
            docstring = methodspec[method]['description']
            for param in methodspec[method].get('parameters', list()):
                param['type'] = param['type'] if 'type' in param else str(
                    param.get('$ref', 'unknown'))
                docstring += """
                :param %(name)s: %(description)s required %(required)s
                :type %(name)s: %(type)s""" % param
            api.__doc__ = docstring
        return swagger


class PortalClient(JSConfigBase, Resource):
    def __init__(self, instance, data=None, parent=None):
        if not data:
            data = {}
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE)
        cfg = self.config.data
        ip = cfg['ip']
        port = cfg['port']
        Resource.__init__(self, ip, port, "/restmachine")
