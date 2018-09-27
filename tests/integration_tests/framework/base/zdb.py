from jumpscale import j
import copy
from termcolor import colored



class ZDB:

    def __init__(self, node, guid=None, data=None):
        self.guid = guid 
        self.data = data
        self.node_sal = node
        self.zerodb_sal = None

    @property
    def _zerodb_sal(self):
        data = self.data.copy()
        return self.node_sal.primitives.from_dict('zerodb', data)

    def install(self):
        self.zerodb_sal = self._zerodb_sal
        self._deploy()
        self.data['nodePort'] = self.zerodb_sal.node_port
        self.data['ztIdentity'] = self.zerodb_sal.zt_identity

    def _deploy(self):
        self.zerodb_sal.deploy()

    def start(self):
        """
        start zerodb server
        """
        self.zerodb_sal.start()

    def stop(self):
        """
        stop zerodb server
        """
        self.zerodb_sal.stop()

    def upgrade(self):
        """
        upgrade 0-db
        """
        self.stop()
        self.start()

    def info(self):
        """
        Return disk information
        """
        return self.zerodb_sal.info

    def namespace_list(self):
        """
        List namespace
        :return: list of namespaces ex: ['namespace1', 'namespace2']
        """
        return self.zerodb_sal.namespaces.list()

    def namespace_info(self, name):
        """
        Get info of namespace
        :param name: namespace name
        :return: dict
        """
        return self.zerodb_sal.namespaces[name].info().to_dict()

    def namespace_url(self, name):
        """
        Get url of the namespace
        :param name: namespace name
        :return: dict
        """
        return self.zerodb_sal.namespaces[name].url

    def namespace_private_url(self, name):
        """
        Get private url of the namespace
        :param name: namespace name
        :return: dict
        """       
        return self.zerodb_sal.namespaces[name].private_url

    def namespace_create(self, name, size=None, password=None, public=True):
        """
        Create a namespace and set the size and secret
        :param name: namespace name
        :param size: namespace size
        :param password: namespace password
        :param public: namespace public status
        """
        self.zerodb_sal.namespaces.add(name=name, size=size, password=password, public=public)
        self._deploy()

    def namespace_set(self, name, prop, value):
        """
        Set a property of a namespace
        :param name: namespace name
        :param prop: property name
        :param value: property value
        """
        self.zerodb_sal.namespaces[name].set_property(prop, value)

    def namespace_delete(self, name):
        """
        Delete a namespace
        """
        self.zerodb_sal.namespaces.remove(name)
        self._deploy()
