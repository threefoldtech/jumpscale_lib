"""
Auto-generated class for Signature
"""
from datetime import datetime
from six import string_types
from Jumpscale import j
from . import client_support




class Signature( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type date: datetime
        :type publicKey: str
        :type signature: str
        :type signedBy: str
        :rtype: Signature
        """

        return Signature(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Signature'
        data = json or kwargs

        # set attributes
        data_types = [datetime]
        self.date = client_support.set_property('date', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.publicKey = client_support.set_property('publicKey', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.signature = client_support.set_property('signature', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.signedBy = client_support.set_property('signedBy', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
