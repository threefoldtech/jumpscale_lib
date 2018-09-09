"""
Auto-generated class for UserAPIKey
"""
from .Label import Label
from six import string_types
from Jumpscale import j
from . import client_support




class UserAPIKey( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type apikey: str
        :type applicationid: str
        :type label: Label
        :type scopes: list[str]
        :type username: str
        :rtype: UserAPIKey
        """

        return UserAPIKey(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'UserAPIKey'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.apikey = client_support.set_property('apikey', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.applicationid = client_support.set_property(
            'applicationid', data, data_types, False, [], False, True, class_name)
        data_types = [Label]
        self.label = client_support.set_property('label', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.scopes = client_support.set_property('scopes', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.username = client_support.set_property('username', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
