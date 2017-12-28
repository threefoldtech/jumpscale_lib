"""
Auto-generated class for EditMilestoneOption
"""
from datetime import datetime
from six import string_types

from . import client_support


class EditMilestoneOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type description: str
        :type due_on: datetime
        :type state: str
        :type title: str
        :rtype: EditMilestoneOption
        """

        return EditMilestoneOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'EditMilestoneOption'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.description = client_support.set_property(
            'description', data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.due_on = client_support.set_property('due_on', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.state = client_support.set_property('state', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.title = client_support.set_property('title', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
