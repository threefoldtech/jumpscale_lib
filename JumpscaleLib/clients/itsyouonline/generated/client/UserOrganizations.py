"""
Auto-generated class for UserOrganizations
"""
from six import string_types
from Jumpscale import j
from . import client_support




class UserOrganizations( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type member: list[str]
        :type owner: list[str]
        :rtype: UserOrganizations
        """

        return UserOrganizations(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'UserOrganizations'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.member = client_support.set_property('member', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.owner = client_support.set_property('owner', data, data_types, False, [], True, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
