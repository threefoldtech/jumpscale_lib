"""
Auto-generated class for RegistryEntry
"""
from six import string_types
from Jumpscale import j
from . import client_support




class RegistryEntry( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type Key: str
        :type Value: str
        :rtype: RegistryEntry
        """

        return RegistryEntry(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'RegistryEntry'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.Key = client_support.set_property('Key', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.Value = client_support.set_property('Value', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
