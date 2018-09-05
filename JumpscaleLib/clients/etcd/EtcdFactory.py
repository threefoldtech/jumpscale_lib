""" A Jumpscale-configurable wrapper around the python3 etcd client library

    configuration file options will be in {[myconfig].path}/j.clients.etcd
"""

import uuid

class EtcFactory:

    __jslocation__ = "j.clients.etcd"
    __jsbase__ = 'j.tools.configmanager._base_class_configs'

    @property
    def _child_class(self):
        return self._jsbase(('EtcdClient',
                             'JumpscaleLib.clients.etcd.EtcdClient'))

    def configure(self, instance="main", addr="localhost",
                                         port=2379,
                  ):
        """ :param instance:
            :param addr:
            :param port:
            :return:
        """

        if port is None:
            raise InputError("port cannot be None")

        data = {}
        data["addr"] = addr
        data["port"] = str(port)

        return self.get(instance=instance, data=data, create=True,
                        interactive=False)

    def test(self,reset=True):
        """
        js_shell 'j.clients.etcd.test()'

        """

        # create a random namespace
        def random_string(length=10):
            return str(uuid.uuid4()).replace('-', '')[:length]

        cl1 = self.get()
        import IPython
        IPython.embed()
