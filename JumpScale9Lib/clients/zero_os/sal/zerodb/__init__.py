from .zerodb import Zerodb
from ..abstracts import DynamicCollection


class Zerodbs(DynamicCollection):
    def __init__(self, node):
        self.node = node

    def get(self, name):
        """
        Get zerodb object and load data from reality

        :param name: Name of the zerodb
        :type name: str

        :return: Zerodb object
        :rtype: Zerodb object
        """
        zdb = Zerodb(self.node, name)
        zdb.load_from_reality()
        return zdb

    def list(self):
        """
        list zerodb objects

        :return: list of Zerodb object
        :rtype: list
        """
        zdbs = []
        for container in self.node.containers.list():
            if container.name.startswith('zdb_'):
                zdb = Zerodb(self.node, container.name.replace('zdb_', ''))
                zdb.load_from_reality(container)
                zdbs.append(zdb)
        return zdbs

    def create(self, name, path=None, mode='user', sync=False, admin='', node_port=9900):
        """
        Create zerodb object

        To deploy zerodb invoke .deploy method

        :param name: Name of the zerodb
        :type name: str
        :param path: path zerodb stores data on
        :type path: str
        :param mode: zerodb running mode
        :type mode: str
        :param sync: zerodb sync
        :type sync: bool
        :param admin: zerodb admin password
        :type admin: str

        :return: Zerodb object
        :rtype: Zerodb object
        """
        return Zerodb(self.node, name, path, mode, sync, admin, node_port)
