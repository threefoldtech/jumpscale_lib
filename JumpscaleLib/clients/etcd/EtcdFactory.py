""" A Jumpscale-configurable wrapper around the python3 etcd client library

    configuration file options will be in {[myconfig].path}/j.clients.etcd

    unit tests are in core9 tests/jumpscale_tests/test11_keyvalue_stores.py
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
