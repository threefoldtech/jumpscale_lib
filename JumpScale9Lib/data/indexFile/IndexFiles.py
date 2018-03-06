
from js9 import j
# from pprint import pprint as print

from .IndexFile import IndexFile
JSBASE = j.application.jsbase_get_class()


class IndexDB(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.indexfile"
        self.basepath = "%s/indexfile/" % (j.dirs.VARDIR)
        JSBASE.__init__(self)

    def get(self, name, path=None, nrbytes=4):
        if path is None:
            path = j.sal.fs.joinPaths(self.basepath, name.lower().strip())

        return IndexFile(path, nrbytes=nrbytes)

    def test(self):
        """
        js9 'j.data.indexfile.test()'

        """
        # test set
        index = self.get("test")
        for i in range(10):
            data = str(i) * index.nrbytes
            index.set(i, data)

        try:
            index.set(11, b"data too long")
            assert False
        except j.exceptions.Input:
            # should raise
            pass

            # test get
        for i in range(10):
            expected = (str(i) * index.nrbytes).encode()
            actual = index.get(i)
            assert expected == actual

        # test iterate over all
        actual = []

        def walk(pos, data, result):
            actual.append(data)
        index.iterate(walk, 0, 0)
        expected = []
        for i in range(10):
            expected.append((str(i) * index.nrbytes).encode())
        print("expected:", expected)
        print("actual:  ", actual)
        assert expected == actual

        # test iterate over a portion
        actual = []

        def walk(pos, data, result):
            actual.append(data)
        index.iterate(walk, 4, 9)
        expected = []
        for i in range(4, 9):
            expected.append((str(i) * index.nrbytes).encode())
        print("expected:", expected)
        print("actual:  ", actual)
        assert expected == actual

        j.sal.fs.remove(index.path)
