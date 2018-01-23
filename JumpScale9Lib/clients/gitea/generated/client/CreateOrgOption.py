"""
Auto-generated class for CreateOrgOption
"""
from six import string_types

from . import client_support


class CreateOrgOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type description: str
        :type full_name: str
        :type location: str
        :type username: str
        :type website: str
        :rtype: CreateOrgOption
        """

        return CreateOrgOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CreateOrgOption'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.description = client_support.set_property(
            'description', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.full_name = client_support.set_property('full_name', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.location = client_support.set_property('location', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.username = client_support.set_property('username', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.website = client_support.set_property('website', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)