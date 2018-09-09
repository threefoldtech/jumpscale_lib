"""
Auto-generated class for userview
"""
from .Address import Address
from .Avatar import Avatar
from .BankAccount import BankAccount
from .DigitalAssetAddress import DigitalAssetAddress
from .EmailAddress import EmailAddress
from .FacebookAccount import FacebookAccount
from .GithubAccount import GithubAccount
from .Ownerof import Ownerof
from .Phonenumber import Phonenumber
from .PublicKey import PublicKey
from six import string_types
from Jumpscale import j
from . import client_support




class userview( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type addresses: list[Address]
        :type avatar: list[Avatar]
        :type bankaccounts: list[BankAccount]
        :type digitalwallet: DigitalAssetAddress
        :type emailaddresses: list[EmailAddress]
        :type facebook: FacebookAccount
        :type firstname: str
        :type github: GithubAccount
        :type lastname: str
        :type organizations: list[str]
        :type ownerof: Ownerof
        :type phonenumbers: list[Phonenumber]
        :type publicKeys: list[PublicKey]
        :type username: str
        :type validatedemailaddresses: list[EmailAddress]
        :type validatedphonenumbers: list[Phonenumber]
        :rtype: userview
        """

        return userview(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'userview'
        data = json or kwargs

        # set attributes
        data_types = [Address]
        self.addresses = client_support.set_property('addresses', data, data_types, False, [], True, True, class_name)
        data_types = [Avatar]
        self.avatar = client_support.set_property('avatar', data, data_types, False, [], True, True, class_name)
        data_types = [BankAccount]
        self.bankaccounts = client_support.set_property(
            'bankaccounts', data, data_types, False, [], True, True, class_name)
        data_types = [DigitalAssetAddress]
        self.digitalwallet = client_support.set_property(
            'digitalwallet', data, data_types, False, [], False, True, class_name)
        data_types = [EmailAddress]
        self.emailaddresses = client_support.set_property(
            'emailaddresses', data, data_types, False, [], True, True, class_name)
        data_types = [FacebookAccount]
        self.facebook = client_support.set_property('facebook', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.firstname = client_support.set_property('firstname', data, data_types, False, [], False, True, class_name)
        data_types = [GithubAccount]
        self.github = client_support.set_property('github', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.lastname = client_support.set_property('lastname', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.organizations = client_support.set_property(
            'organizations', data, data_types, False, [], True, True, class_name)
        data_types = [Ownerof]
        self.ownerof = client_support.set_property('ownerof', data, data_types, False, [], False, True, class_name)
        data_types = [Phonenumber]
        self.phonenumbers = client_support.set_property(
            'phonenumbers', data, data_types, False, [], True, True, class_name)
        data_types = [PublicKey]
        self.publicKeys = client_support.set_property(
            'publicKeys', data, data_types, False, [], True, False, class_name)
        data_types = [string_types]
        self.username = client_support.set_property('username', data, data_types, False, [], False, True, class_name)
        data_types = [EmailAddress]
        self.validatedemailaddresses = client_support.set_property(
            'validatedemailaddresses', data, data_types, False, [], True, True, class_name)
        data_types = [Phonenumber]
        self.validatedphonenumbers = client_support.set_property(
            'validatedphonenumbers', data, data_types, False, [], True, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
