"""
Auto-generated class for Authorization
"""
from .AuthorizationMap import AuthorizationMap
from six import string_types
from Jumpscale import j
from . import client_support




class Authorization( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type addresses: list[AuthorizationMap]
        :type bankaccounts: list[AuthorizationMap]
        :type emailaddresses: list[AuthorizationMap]
        :type facebook: bool
        :type github: bool
        :type grantedTo: str
        :type organizations: list[str]
        :type phonenumbers: list[AuthorizationMap]
        :type publicKeys: list[AuthorizationMap]
        :type username: str
        :rtype: Authorization
        """

        return Authorization(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Authorization'
        data = json or kwargs

        # set attributes
        data_types = [AuthorizationMap]
        self.addresses = client_support.set_property('addresses', data, data_types, False, [], True, False, class_name)
        data_types = [AuthorizationMap]
        self.bankaccounts = client_support.set_property(
            'bankaccounts', data, data_types, False, [], True, False, class_name)
        data_types = [AuthorizationMap]
        self.emailaddresses = client_support.set_property(
            'emailaddresses', data, data_types, False, [], True, False, class_name)
        data_types = [bool]
        self.facebook = client_support.set_property('facebook', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.github = client_support.set_property('github', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.grantedTo = client_support.set_property('grantedTo', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.organizations = client_support.set_property(
            'organizations', data, data_types, False, [], True, True, class_name)
        data_types = [AuthorizationMap]
        self.phonenumbers = client_support.set_property(
            'phonenumbers', data, data_types, False, [], True, False, class_name)
        data_types = [AuthorizationMap]
        self.publicKeys = client_support.set_property(
            'publicKeys', data, data_types, False, [], True, False, class_name)
        data_types = [string_types]
        self.username = client_support.set_property('username', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
