import requests

from js9 import j

NODE_PREFIX = '/nodes'
FARMER_PREFIX = '/farmers'


def _etcd_node_key(node_id):
    return '%s/%s' % (NODE_PREFIX, node_id)


def _etcd_farmer_key(farmer_id):
    return '%s/%s' % (FARMER_PREFIX, farmer_id)


class CapacityRegistration:

    def __init__(self):
        # TODO: need to hardcode location of the etcd cluster for tf capacity
        etcd = j.clients.etcd.get('zeroos-capacity', data={'host': 'localhost', 'port': 2379}).api
        self.nodes = NodeRegistration(etcd)
        self.farmer = FarmerRegistration(etcd)


class NodeRegistration:

    def __init__(self, etcd):
        self._etcd = etcd

    def register(self, capacity, ttl=None):
        """
        register capacity from a node

        :param capacity: capacity of the node
        :type capacity_obj: Capacity
        :param ttl: if set, the capacity will be only registered to ttl seconds
        :type ttl: int
        """
        if not isinstance(capacity, Capacity):
            raise TypeError("capacity should be a Capacity object not %s" % type(capacity))

        if capacity.location is None:
            resp = requests.get('http://geoip.nekudo.com/api/en/full')
            if resp.status_code == 200:
                data = resp.json()
                capacity.location = Location(
                    continent=data.get('continent').get('names').get('en'),
                    country=data.get('country').get('names').get('en'),
                    city=data.get('city').get('names').get('en'),
                    latitude=data.get('location').get('latitude'),
                    longitude=data.get('location').get('longitude')
                )

        lease = None
        if ttl:
            lease = self._etcd.lease(ttl)

        key = _etcd_node_key(capacity.node_id)
        self._etcd.put(key, capacity.serialize(), lease)

    def list(self, country=None):
        """
        list all the capacity, optionally filter per country.
        returns a list of capacity object

        :param country: [description], defaults to None
        :param country: [type], optional
        :return: sequence of Capacity object
        :rtype: sequence
        """
        for blob, _ in self._etcd.get_prefix(NODE_PREFIX):
            capacity = Capacity.deserialize(blob)
            if country and capacity.location.country.lower() != country.lower():
                continue
            yield capacity

    def get(self, node_id):
        """
        return the capacity for a single node

        :param node_id: unique node ID
        :type node_id: str
        :return: Capacity object
        :rtype: Capacity
        """

        key = _etcd_node_key(node_id)
        blob, _ = self._etcd.get(key)
        if not blob:
            raise NodeNotFoundError("node '%s' not found" % node_id)
        return Capacity.deserialize(blob)

    def search(self, country=None, mru=None, cru=None, hru=None, sru=None):
        """
        search based on country and minimum resource unit available

        :param country: if set, search for capacity in the specified country, defaults to None
        :param country: str, optional
        :param mru: minimal memory ressource unit, defaults to None
        :param mru: int, optional
        :param cru: minimal CPU resource unit, defaults to None
        :param cru: int, optional
        :param hru: minimal HDD resource unit, defaults to None
        :param hru: int, optional
        :param sru: minimal SSD ressource unit defaults to None
        :param sru: int, optional
        :return: sequence of Capacity object matching the query
        :rtype: sequence
        """
        for capacity in self.list(country=country):
            if mru and capacity.mru < mru:
                continue
            if cru and capacity.cru < cru:
                continue
            if hru and capacity.hru < hru:
                continue
            if sru and capacity.sru < sru:
                continue
            yield capacity


class FarmerRegistration:

    def __init__(self, etcd):
        self._etcd = etcd

    def create(self, name, iyo_account, wallet_addresses=None):
        raise NotImplementedError()
        # return Farmer(name=name, iyo_account=iyo_account, wallet_addresses=wallet_addresses)

    def register(self, farmer):
        if not isinstance(farmer, Farmer):
            raise TypeError("farmer need to be a Farmer object, not %s" % type(farmer))
        key = _etcd_farmer_key(farmer.id)
        self._etcd.put(key, farmer.serialize())

    def list(self):
        for blob, _ in self._etcd.get_prefix(FARMER_PREFIX):
            yield Farmer.deserialize(blob)

    def get(self, id):
        blob, _ = self._etcd.get(_etcd_farmer_key(id))
        if not blob:
            raise FarmerNotFoundError("farmer '%s' not found" % id)
        return Farmer.deserialize(blob)


class Serializer:
    """
    Child of this class get ability do serialize and deserialize the child object

    child class need to implement the _to_dict method to be compatible with this base class
    """

    def serialize(self):
        """
        Create a string representation of this object

        This is used when storing data to the capacity database

        :return: serialized version of this object
        :rtype: str
        """
        return j.data.serializer.yaml.dumps(self._to_dict())

    @classmethod
    def deserialize(cls, blob):
        """
        create an object from its serialized form

        This is used when loading data from the capacity database

        :param blob: serialized form of the object
        :type blob: str or bytes
        :return: object
        :rtype: child type
        """
        d = j.data.serializer.yaml.loads(blob)
        return cls(**d)

    def _to_dict(self):
        """
        child class need to implement this method to make the serialization works

        the keys used in dictionary returned need to be the same as the attribute of the child class
        """

        raise NotImplementedError()


class Capacity(Serializer):
    """
    Represent the ressource units of a zero-os node
    """

    def __init__(self, node_id, farmer, location, cru, mru, hru, sru, robot_address, os_version):
        self.node_id = node_id
        self.location = location
        self.farmer = farmer
        self.cru = cru
        self.mru = mru
        self.hru = hru
        self.sru = sru
        self.robot_address = robot_address
        self.os_version = os_version

    @classmethod
    def deserialize(cls, blob):
        d = j.data.serializer.yaml.loads(blob)
        d['location'] = Location(**d['location'])
        return cls(**d)

    def _to_dict(self):
        return {
            'node_id': self.node_id,
            'location': self.location._to_dict() if self.location else None,
            'farmer': self.farmer,
            'cru': self.cru,
            'mru': self.mru,
            'hru': self.hru,
            'sru': self.sru,
            'robot_address': self.robot_address,
            'os_version': self.os_version,
        }

    def __repr__(self):
        return self.serialize()


class Location(Serializer):
    """
    Location of a node
    """

    def __init__(self, continent, country, city, latitude, longitude):
        self.continent = continent
        self.country = country
        self.city = city
        self.latitude = latitude
        self.longitude = longitude

    def _to_dict(self):
        return {
            'continent': self.continent,
            'country': self.country,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    def __repr__(self):
        return self.serialize()


class Farmer(Serializer):

    """
    Represent a threefold Farmer
    """

    def __init__(self, id, name, iyo_account, wallet_addresses=None):
        self.id = id
        self.name = name
        self.iyo_account = iyo_account
        self.wallet_addresses = wallet_addresses or []

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'wallet_addresses': self.wallet_addresses,
            'iyo_account': self.iyo_account
        }

    def __repr__(self):
        return self.serialize()


class FarmerNotFoundError(KeyError):
    pass


class NodeNotFoundError(KeyError):
    pass
