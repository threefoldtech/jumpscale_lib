from js9 import j
import os

# from JumpScale9Lib.data.markdown.mistune import *

# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters import HtmlFormatter

import copy

from .MarkdownDocument import *
from .MarkdownComponents import *
JSBASE = j.application.jsbase_get_class()


class MarkdownFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.markdown"
        JSBASE.__init__(self)

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))


    def document_get(self, content="", path=""):
        """
        returns a tool which allows easy creation of a markdown document
        """
        return MarkdownDocument(content, path)

    def mdtable_get(self):
        return MDTable()

    def mddata_get(self):
        return MDData()


    def test(self):
        '''
        js9 'j.data.markdown.test()'
        '''
        # from .tests.test1 import test
        # test()
        # from .tests.test2 import test
        # test()        
        # from .tests.test3 import test
        # test()        
        from .tests.test4 import test
        test()

