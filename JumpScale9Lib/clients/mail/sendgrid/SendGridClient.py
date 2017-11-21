import sendgrid
import os
from sendgrid.helpers.mail import Email, Content, Mail


class SendGridClient:

    def __init__(self):
        self.__jslocation__ = "j.clients.sendgrid"
    
    def send(self, sender, recipient, subject, message, message_type="text/plain", api_key=None):
        """
        @param sender: the sender of the email
        @type sender: string
        @param recipient: the recipient of the email
        @type recipient: string
        @param subject: subject of the email
        @type subject: string
        @param message: content of the email
        @type message: string
        @param message_type: mime type of the email content
        @type message_type:  string
        @param api_key: the api key of sendgrid
        @type api_key: string
        """
        api_key = api_key or os.environ.get('SENDGRID_API_KEY', None)

        if api_key is None:
            raise RuntimeError('Make sure to export SENDGRID_API_KEY or pass your api key')
        sg = sendgrid.SendGridAPIClient(apikey=api_key)
        from_email = Email(sender)
        to_email = Email(recipient)
        content = Content(message_type, message)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return response.status_code, response.body

    def test(self):
        SENDER = "test@example.com"
        RECIPENT = "test@example.com"
        SUBJECT = "Sending with SendGrid is Fun"
        MESSAGE_TYPE = "text/plain"
        MESSAGE = "and easy to do anywhere, even with Python"
        statCode , body = self.send(SENDER, RECIPENT, SUBJECT, MESSAGE, MESSAGE_TYPE)
        print(statCode)


