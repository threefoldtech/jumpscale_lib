"""
Auto-generated class for Avatar
"""
from .Label import Label
from six import string_types
from Jumpscale import j
from . import client_support




class Avatar( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type label: Label
        :type source: str
        :rtype: Avatar
        """

        return Avatar(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Avatar'
        data = json or kwargs

        # set attributes
        data_types = [Label]
        self.label = client_support.set_property('label', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.source = client_support.set_property('source', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
