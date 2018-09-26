from jumpscale import j
import copy
from termcolor import colored



class ZDB:

    def __init__(self, node, guid=None, data=None):
        self.guid = guid 
        self.data = data
        self.node_sal = node

    @property
    def _zerodb_sal(self):
        data = self.data.copy()
        return self.node_sal.primitives.from_dict('zerodb', data)

    def _deploy(self):
        zerodb_sal = self._zerodb_sal
        zerodb_sal.deploy()
        self.data['nodePort'] = zerodb_sal.node_port
        self.data['ztIdentity'] = zerodb_sal.zt_identity

    def install(self):
        print(colored('Installing zerodb %s' % self.data['name'], 'white'))

        self._deploy()

    def start(self):
        """
        start zerodb server
        """
        print(colored('Starting zerodb %s' % self.data['name'], 'white'))
        self._zerodb_sal.deploy()

    def stop(self):
        """
        stop zerodb server
        """
        print(colored('Stopping zerodb %s' % self.data['name'], 'white'))
        self._zerodb_sal.stop()

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
        return self._zerodb_sal.info

    def namespace_list(self):
        """
        List namespace
        :return: list of namespaces ex: ['namespace1', 'namespace2']
        """
        return self.data['namespaces']

    def namespace_info(self, name):
        """
        Get info of namespace
        :param name: namespace name
        :return: dict
        """
        if not self._namespace_exists_update_delete(name):
            raise LookupError('Namespace {} doesn\'t exist'.format(name))
        return self._zerodb_sal.namespaces[name].info().to_dict()

    def namespace_url(self, name):
        """
        Get url of the namespace
        :param name: namespace name
        :return: dict
        """
        if not self._namespace_exists_update_delete(name):
            raise LookupError('Namespace {} doesn\'t exist'.format(name))
        return self._zerodb_sal.namespaces[name].url

    def namespace_private_url(self, name):
        """
        Get private url of the namespace
        :param name: namespace name
        :return: dict
        """       
        if not self._namespace_exists_update_delete(name):
            raise LookupError('Namespace {} doesn\'t exist'.format(name))
        return self._zerodb_sal.namespaces[name].private_url

    def namespace_create(self, name, size=None, password=None, public=True):
        """
        Create a namespace and set the size and secret
        :param name: namespace name
        :param size: namespace size
        :param password: namespace password
        :param public: namespace public status
        """
        
        if self._namespace_exists_update_delete(name):
            raise ValueError('Namespace {} already exists'.format(name))
        
        print(colored("create namespace %s"%name, 'white'))
        self.data['namespaces'].append({'name': name, 'size': size, 'password': password, 'public': public})
        self._zerodb_sal.deploy()

    def namespace_set(self, name, prop, value):
        """
        Set a property of a namespace
        :param name: namespace name
        :param prop: property name
        :param value: property value
        """

        if not self._namespace_exists_update_delete(name, prop, value):
            raise LookupError('Namespace {} doesn\'t exist'.format(name))
        self._zerodb_sal.deploy()

    def namespace_delete(self, name):
        """
        Delete a namespace
        """
        if not self._namespace_exists_update_delete(name, delete=True):
            print(colored("namespace already doesn't exist", 'red'))
            return
        print(colored("delete namespace %s"%name,'white'))
        self._zerodb_sal.deploy()

    def connection_info(self):
        return {
            'ip': self.node_sal.public_addr,
            'port': self.data['nodePort']
        }

    def _namespace_exists_update_delete(self, name, prop=None, value=None, delete=False):
        if prop and delete:
            raise ValueError('Can\'t set property and delete at the same time')
        if prop and prop not in ['size', 'password', 'public']:
            raise ValueError('Property must be size, password, or public')

        for namespace in self.data['namespaces']:
            if namespace['name'] == name:
                if prop:
                    if prop not in ['size', 'password', 'public']:
                        raise ValueError('Property must be size, password, or public')
                    namespace[prop] = value
                if delete:
                    self.data['namespaces'].remove(namespace)
                return True
        return False
