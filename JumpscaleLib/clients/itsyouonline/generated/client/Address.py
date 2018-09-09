"""
Auto-generated class for Address
"""
from .Label import Label
from six import string_types
from Jumpscale import j
from . import client_support




class Address( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type city: str
        :type country: str
        :type label: Label
        :type nr: str
        :type other: str
        :type postalcode: str
        :type street: str
        :rtype: Address
        """

        return Address(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Address'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.city = client_support.set_property('city', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.country = client_support.set_property('country', data, data_types, False, [], False, True, class_name)
        data_types = [Label]
        self.label = client_support.set_property('label', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.nr = client_support.set_property('nr', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.other = client_support.set_property('other', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.postalcode = client_support.set_property(
            'postalcode', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.street = client_support.set_property('street', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
