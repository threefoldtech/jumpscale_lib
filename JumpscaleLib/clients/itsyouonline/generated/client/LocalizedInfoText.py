"""
Auto-generated class for LocalizedInfoText
"""
from six import string_types
from Jumpscale import j
from . import client_support




class LocalizedInfoText( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type langkey: str
        :type text: str
        :rtype: LocalizedInfoText
        """

        return LocalizedInfoText(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'LocalizedInfoText'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.langkey = client_support.set_property('langkey', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.text = client_support.set_property('text', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
