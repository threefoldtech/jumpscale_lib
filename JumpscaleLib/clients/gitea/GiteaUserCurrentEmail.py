import json
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class GiteaUserCurrentEmail(JSBASE):
    def __init__(
        self,
        client,
        user,
        primary=False,
        verified=False,
        email=None,
    ):
        self.client = client
        self.user = user
        self.primary = primary
        self.verified = verified
        self.email = email

        JSBASE.__init__(self)

    @property
    def data(self):
        return {
            'email': self.email,
            'verified': self.verified,
            'primary': self.primary
        }

    def __repr__(self):
        return '\n<Email>\n%s' % json.dumps(self.data, indent=4)

    __str__ = __repr__