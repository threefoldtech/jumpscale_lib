"""
Auto-generated class for OrganizationAPIKey
"""
from .Label import Label
from six import string_types
from Jumpscale import j
from . import client_support




class OrganizationAPIKey( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type callbackURL: str
        :type clientCredentialsGrantType: bool
        :type label: Label
        :type secret: str
        :rtype: OrganizationAPIKey
        """

        return OrganizationAPIKey(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'OrganizationAPIKey'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.callbackURL = client_support.set_property(
            'callbackURL', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.clientCredentialsGrantType = client_support.set_property(
            'clientCredentialsGrantType', data, data_types, False, [], False, False, class_name)
        data_types = [Label]
        self.label = client_support.set_property('label', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.secret = client_support.set_property('secret', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
