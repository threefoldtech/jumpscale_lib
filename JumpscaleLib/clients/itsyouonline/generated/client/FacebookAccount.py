"""
Auto-generated class for FacebookAccount
"""
from six import string_types
from Jumpscale import j
from . import client_support




class FacebookAccount( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type id: int
        :type link: str
        :type name: str
        :type picture: str
        :rtype: FacebookAccount
        """

        return FacebookAccount(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'FacebookAccount'
        data = json or kwargs

        # set attributes
        data_types = [int]
        self.id = client_support.set_property('id', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.link = client_support.set_property('link', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.name = client_support.set_property('name', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.picture = client_support.set_property('picture', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
