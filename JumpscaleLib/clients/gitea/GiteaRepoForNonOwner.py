import json
from jumpscale import j

from .GiteaRepo import GiteaRepo

JSBASE = j.application.jsbase_get_class()


class GiteaRepoForNonOwner(GiteaRepo):
    pass
