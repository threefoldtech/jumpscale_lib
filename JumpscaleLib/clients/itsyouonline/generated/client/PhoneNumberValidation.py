"""
Auto-generated class for PhoneNumberValidation
"""
from six import string_types
from Jumpscale import j
from . import client_support




class PhoneNumberValidation( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type validationkey: str
        :rtype: PhoneNumberValidation
        """

        return PhoneNumberValidation(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'PhoneNumberValidation'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.validationkey = client_support.set_property(
            'validationkey', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
