from js9 import j

from JumpScale9Lib.data.capnp.Capnp import Capnp
base = Capnp().getModelBaseClassCollection()


class UserGroupCollection(base):
    """
    """

    def find(self, name="", state=""):
        """
        @param state
            new
            ok
            error
            disabled
        """
        #@TODO: *1 needs to be properly implemented
        res = []
        for key in self._list_keys(name, state):
            res.append(self.get(key))
        return res
