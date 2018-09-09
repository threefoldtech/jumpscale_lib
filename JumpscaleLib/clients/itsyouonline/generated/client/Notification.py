"""
Auto-generated class for Notification
"""
from .ContractSigningRequest import ContractSigningRequest
from .JoinOrganizationInvitation import JoinOrganizationInvitation
from .MissingScopes import MissingScopes
from Jumpscale import j
from . import client_support




class Notification( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type approvals: list[JoinOrganizationInvitation]
        :type contractRequests: list[ContractSigningRequest]
        :type invitations: list[JoinOrganizationInvitation]
        :type missingscopes: list[MissingScopes]
        :rtype: Notification
        """

        return Notification(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Notification'
        data = json or kwargs

        # set attributes
        data_types = [JoinOrganizationInvitation]
        self.approvals = client_support.set_property('approvals', data, data_types, False, [], True, True, class_name)
        data_types = [ContractSigningRequest]
        self.contractRequests = client_support.set_property(
            'contractRequests', data, data_types, False, [], True, True, class_name)
        data_types = [JoinOrganizationInvitation]
        self.invitations = client_support.set_property(
            'invitations', data, data_types, False, [], True, True, class_name)
        data_types = [MissingScopes]
        self.missingscopes = client_support.set_property(
            'missingscopes', data, data_types, False, [], True, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
