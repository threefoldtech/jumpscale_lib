from js9 import j
import toml

import copy

from .DocBase import DocBase

class HtmlPage(DocBase):
    """
    """

    def __init__(self, path, name, docsite):
        DocBase.__init__(self, path, name, docsite)

    @property
    def content_clean(self):
        return self.content

    @property
    def title(self):
        self.error_raise("Could not find title in doc, need to implement")

    def __repr__(self):
        return "htmlpage:%s:%s" % (self.name, self.path)


