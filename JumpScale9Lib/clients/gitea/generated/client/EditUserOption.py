"""
Auto-generated class for EditUserOption
"""
from six import string_types

from . import client_support


class EditUserOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type active: bool
        :type admin: bool
        :type allow_git_hook: bool
        :type allow_import_local: bool
        :type email: str
        :type full_name: str
        :type location: str
        :type login_name: str
        :type max_repo_creation: int
        :type password: str
        :type source_id: int
        :type website: str
        :rtype: EditUserOption
        """

        return EditUserOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'EditUserOption'
        data = json or kwargs

        # set attributes
        data_types = [bool]
        self.active = client_support.set_property('active', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.admin = client_support.set_property('admin', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.allow_git_hook = client_support.set_property(
            'allow_git_hook', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.allow_import_local = client_support.set_property(
            'allow_import_local', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.email = client_support.set_property('email', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.full_name = client_support.set_property('full_name', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.location = client_support.set_property('location', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.login_name = client_support.set_property(
            'login_name', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.max_repo_creation = client_support.set_property(
            'max_repo_creation', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.password = client_support.set_property('password', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.source_id = client_support.set_property('source_id', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.website = client_support.set_property('website', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
