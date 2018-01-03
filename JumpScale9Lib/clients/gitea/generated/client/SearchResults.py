"""
Auto-generated class for SearchResults
"""
from .Repository import Repository

from . import client_support


class SearchResults(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type data: list[Repository]
        :type ok: bool
        :rtype: SearchResults
        """

        return SearchResults(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'SearchResults'
        data = json or kwargs

        # set attributes
        data_types = [Repository]
        self.data = client_support.set_property('data', data, data_types, False, [], True, False, class_name)
        data_types = [bool]
        self.ok = client_support.set_property('ok', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
