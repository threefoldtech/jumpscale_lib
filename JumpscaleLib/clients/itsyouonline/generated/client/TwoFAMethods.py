"""
Auto-generated class for TwoFAMethods
"""
from .Phonenumber import Phonenumber
from Jumpscale import j
from . import client_support



class TwoFAMethods( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type sms: list[Phonenumber]
        :type totp: bool
        :rtype: TwoFAMethods
        """

        return TwoFAMethods(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'TwoFAMethods'
        data = json or kwargs

        # set attributes
        data_types = [Phonenumber]
        self.sms = client_support.set_property('sms', data, data_types, False, [], True, True, class_name)
        data_types = [bool]
        self.totp = client_support.set_property('totp', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
