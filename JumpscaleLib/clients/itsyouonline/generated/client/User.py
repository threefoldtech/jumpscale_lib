"""
Auto-generated class for User
"""
from .Address import Address
from .BankAccount import BankAccount
from .DigitalAssetAddress import DigitalAssetAddress
from .EmailAddress import EmailAddress
from .FacebookAccount import FacebookAccount
from .GithubAccount import GithubAccount
from .Phonenumber import Phonenumber
from datetime import datetime
from six import string_types
from Jumpscale import j
from . import client_support




class User( ):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type addresses: list[Address]
        :type bankaccounts: list[BankAccount]
        :type digitalwallet: list[DigitalAssetAddress]
        :type emailaddresses: list[EmailAddress]
        :type expire: datetime
        :type facebook: FacebookAccount
        :type firstname: str
        :type github: GithubAccount
        :type lastname: str
        :type phonenumbers: list[Phonenumber]
        :type publicKeys: list[str]
        :type username: str
        :rtype: User
        """

        return User(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'User'
        data = json or kwargs

        # set attributes
        data_types = [Address]
        self.addresses = client_support.set_property('addresses', data, data_types, False, [], True, True, class_name)
        data_types = [BankAccount]
        self.bankaccounts = client_support.set_property(
            'bankaccounts', data, data_types, False, [], True, True, class_name)
        data_types = [DigitalAssetAddress]
        self.digitalwallet = client_support.set_property(
            'digitalwallet', data, data_types, False, [], True, True, class_name)
        data_types = [EmailAddress]
        self.emailaddresses = client_support.set_property(
            'emailaddresses', data, data_types, False, [], True, True, class_name)
        data_types = [datetime]
        self.expire = client_support.set_property('expire', data, data_types, False, [], False, False, class_name)
        data_types = [FacebookAccount]
        self.facebook = client_support.set_property('facebook', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.firstname = client_support.set_property('firstname', data, data_types, False, [], False, True, class_name)
        data_types = [GithubAccount]
        self.github = client_support.set_property('github', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.lastname = client_support.set_property('lastname', data, data_types, False, [], False, True, class_name)
        data_types = [Phonenumber]
        self.phonenumbers = client_support.set_property(
            'phonenumbers', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.publicKeys = client_support.set_property('publicKeys', data, data_types, False, [], True, True, class_name)
        data_types = [string_types]
        self.username = client_support.set_property('username', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
