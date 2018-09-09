"""
Auto-generated class for UpdateOrganizationOrgMemberShipReqBody
"""
from six import string_types
from Jumpscale import j
from . import client_support




class UpdateOrganizationOrgMemberShipReqBody( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type org: str
        :type role: str
        :rtype: UpdateOrganizationOrgMemberShipReqBody
        """

        return UpdateOrganizationOrgMemberShipReqBody(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'UpdateOrganizationOrgMemberShipReqBody'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.org = client_support.set_property('org', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.role = client_support.set_property('role', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
