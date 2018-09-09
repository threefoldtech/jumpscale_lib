"""
Auto-generated class for DigitalAssetAddress
"""
from .Label import Label
from datetime import datetime
from six import string_types
from Jumpscale import j
from . import client_support




class DigitalAssetAddress( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type address: str
        :type currencysymbol: str
        :type expire: datetime
        :type label: Label
        :type noexpiration: bool
        :rtype: DigitalAssetAddress
        """

        return DigitalAssetAddress(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DigitalAssetAddress'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.address = client_support.set_property('address', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.currencysymbol = client_support.set_property(
            'currencysymbol', data, data_types, False, [], False, True, class_name)
        data_types = [datetime]
        self.expire = client_support.set_property('expire', data, data_types, False, [], False, True, class_name)
        data_types = [Label]
        self.label = client_support.set_property('label', data, data_types, False, [], False, True, class_name)
        data_types = [bool]
        self.noexpiration = client_support.set_property(
            'noexpiration', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
