"""
Auto-generated class for PullRequest
"""
from .Label import Label
from .Milestone import Milestone
from .PRBranchInfo import PRBranchInfo
from .User import User
from datetime import datetime
from six import string_types

from . import client_support


class PullRequest(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type assignee: User
        :type base: PRBranchInfo
        :type body: str
        :type comments: int
        :type created_at: datetime
        :type diff_url: str
        :type head: PRBranchInfo
        :type html_url: str
        :type id: int
        :type labels: list[Label]
        :type merge_base: str
        :type merge_commit_sha: str
        :type mergeable: bool
        :type merged: bool
        :type merged_at: datetime
        :type merged_by: User
        :type milestone: Milestone
        :type number: int
        :type patch_url: str
        :type state: str
        :type title: str
        :type updated_at: datetime
        :type url: str
        :type user: User
        :rtype: PullRequest
        """

        return PullRequest(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'PullRequest'
        data = json or kwargs

        # set attributes
        data_types = [User]
        self.assignee = client_support.set_property('assignee', data, data_types, False, [], False, False, class_name)
        data_types = [PRBranchInfo]
        self.base = client_support.set_property('base', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.body = client_support.set_property('body', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.comments = client_support.set_property('comments', data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.created_at = client_support.set_property(
            'created_at', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.diff_url = client_support.set_property('diff_url', data, data_types, False, [], False, False, class_name)
        data_types = [PRBranchInfo]
        self.head = client_support.set_property('head', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.html_url = client_support.set_property('html_url', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.id = client_support.set_property('id', data, data_types, False, [], False, False, class_name)
        data_types = [Label]
        self.labels = client_support.set_property('labels', data, data_types, False, [], True, False, class_name)
        data_types = [string_types]
        self.merge_base = client_support.set_property(
            'merge_base', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.merge_commit_sha = client_support.set_property(
            'merge_commit_sha', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.mergeable = client_support.set_property('mergeable', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.merged = client_support.set_property('merged', data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.merged_at = client_support.set_property('merged_at', data, data_types, False, [], False, False, class_name)
        data_types = [User]
        self.merged_by = client_support.set_property('merged_by', data, data_types, False, [], False, False, class_name)
        data_types = [Milestone]
        self.milestone = client_support.set_property('milestone', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.number = client_support.set_property('number', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.patch_url = client_support.set_property('patch_url', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.state = client_support.set_property('state', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.title = client_support.set_property('title', data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.updated_at = client_support.set_property(
            'updated_at', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.url = client_support.set_property('url', data, data_types, False, [], False, False, class_name)
        data_types = [User]
        self.user = client_support.set_property('user', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
