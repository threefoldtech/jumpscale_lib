"""
Auto-generated class for Organization
"""
from .RequiredScope import RequiredScope
from six import string_types
from Jumpscale import j
from . import client_support




class Organization( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type dns: list[str]
        :type globalid: str
        :type includes: list[str]
        :type includesuborgsof: list[str]
        :type members: list[str]
        :type orgmembers: list[str]
        :type orgowners: list[str]
        :type owners: list[str]
        :type publicKeys: list[str]
        :type requiredscopes: list[RequiredScope]
        :rtype: Organization
        """

        return Organization(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Organization'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.dns = client_support.set_property('dns', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.globalid = client_support.set_property('globalid', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.includes = client_support.set_property('includes', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.includesuborgsof = client_support.set_property(
            'includesuborgsof', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.members = client_support.set_property('members', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.orgmembers = client_support.set_property('orgmembers', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.orgowners = client_support.set_property('orgowners', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.owners = client_support.set_property('owners', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.publicKeys = client_support.set_property('publicKeys', data, data_types, False, [], True, True, class_name)
        data_types = [RequiredScope]
        self.requiredscopes = client_support.set_property(
            'requiredscopes', data, data_types, False, [], True, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
