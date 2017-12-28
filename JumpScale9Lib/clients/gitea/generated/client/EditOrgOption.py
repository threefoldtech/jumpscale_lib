"""
Auto-generated class for EditOrgOption
"""
from six import string_types

from . import client_support


class EditOrgOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type description: str
        :type full_name: str
        :type location: str
        :type website: str
        :rtype: EditOrgOption
        """

        return EditOrgOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'EditOrgOption'
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
        self.website = client_support.set_property('website', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
