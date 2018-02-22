from js9 import j
from intercom.errors import HttpError
import intercom
intercom.HttpError = HttpError
intercom.__version__ = '3.1.0'

from intercom.client import Client


JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
token_ = "dG9rOmNjNTRlZDFiX2E3OTZfNGFiM185Mjk5X2YzMGQyN2NjODM4ZToxOjA="
"""

class Intercom(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.intercom"
        JSConfigFactory.__init__(self, IntercomClient)


class IntercomClient(JSConfigClient):
    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        self.token = c['token_']
        self.api = Client(personal_access_token=self.token)

    def send_in_app_message(self, body, admin_id, user_id):
        self.api.messages.create(**{
            "message_type": "inapp",
            "body": body,
            "from": {
                "type": "admin",
                "id": admin_id
            },
            "to": {
                "type": "user",
                "id": user_id
            }
        })

    def send_mail_message_from_admin_to_user(self, subject, body, template, admin_id, user_id):
        """
        sending a mail message from an admin to user

        :param subject:(String)  subject of the email
        :param body: (String) body of the email
        :param template: (String) has one of the 2 values "plain", or "personal"
        :param admin_id: (String) id of sender admin
        :param user_id: (String) id of user who will receive the message
        :return:
        """
        self.api.messages.create(**{
            "message_type": "email",
            "subject": subject,
            "body": body,
            "template": template,
            "from": {
                "type": "admin",
                "id": admin_id
            },
            "to": {
                "type": "user",
                "id": user_id
            }
        })



