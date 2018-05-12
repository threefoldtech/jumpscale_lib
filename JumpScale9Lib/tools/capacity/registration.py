import requests

from js9 import j


class CapacityRegistration:

    def __init__(self):
        # TODO: need to hardcode location of the etcd cluster for tf capacity
        mongo = j.clients.mongodb.get('local', data={'host': 'localhost', 'port': 27017, })
        db = mongo.client.capacity
        self.nodes = NodeRegistration(db.nodes)
        self.farmer = FarmerRegistration(db.farmers)


class NodeRegistration:

    def __init__(self, nodes):
        self._nodes = nodes  # mongodb collection

    def register(self, capacity):
        """
        register capacity from a node

        :param capacity: capacity of the node
        :type capacity_obj: Capacity
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

        self._nodes.replace_one({'node_id': capacity.node_id}, capacity.to_dict(), upsert=True)

    def list(self, country=None):
        """
        list all the capacity, optionally filter per country.
        returns a list of capacity object

        :param country: [description], defaults to None
        :param country: [type], optional
        :return: sequence of Capacity object
        :rtype: sequence
        """
        filter = {}
        if country:
            filter['location'] = {'country': country}

        for cap in self._nodes.find(filter):
            yield Capacity.from_dict(cap)

    def get(self, node_id):
        """
        return the capacity for a single node

        :param node_id: unique node ID
        :type node_id: str
        :return: Capacity object
        :rtype: Capacity
        """
        cap = self._nodes.find_one({'node_id': node_id})
        if not cap:
            raise NodeNotFoundError("node '%s' not found" % node_id)
        return Capacity.from_dict(cap)

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
        filter = {}
        if country:
            filter['location.country'] = country
        if mru:
            filter['mru'] = {'$gte': mru}
        if cru:
            filter['cru'] = {'$gte': cru}
        if hru:
            filter['hru'] = {'$gte': hru}
        if sru:
            filter['sru'] = {'$gte': sru}
        print(filter)
        for cap in self._nodes.find(filter):
            yield Capacity.from_dict(cap)

    def all_countries(self):
        """
        yield all the country present in the database

        :return: sequence of country
        :rtype: sequence of string
        """
        countries = self._nodes.distinct('location.country')
        countries.sort(key=lambda x: x)
        for country in countries:
            yield country


class FarmerRegistration:

    def __init__(self, farmers):
        self._farmers = farmers  # mongodb collection

    def create(self, name, iyo_account, wallet_addresses=None):
        raise NotImplementedError()
        # return Farmer(name=name, iyo_account=iyo_account, wallet_addresses=wallet_addresses)

    def register(self, farmer):
        if not isinstance(farmer, Farmer):
            raise TypeError("farmer need to be a Farmer object, not %s" % type(farmer))

        self._farmers.replace_one({'id': farmer.id}, farmer.to_dict(), upsert=True)

    def list(self):
        for farmer in self._farmers.find({}):
            yield Farmer.from_dict(farmer)

    def get(self, id):
        farmer = self._farmers.find_one({'id': id})
        if not farmer:
            raise FarmerNotFoundError("farmer '%s' not found" % id)
        return Farmer.from_dict(farmer)


class Capacity():
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

    def to_dict(self):
        return {
            'node_id': self.node_id,
            'location': self.location.to_dict() if self.location else None,
            'farmer': self.farmer,
            'cru': self.cru,
            'mru': self.mru,
            'hru': self.hru,
            'sru': self.sru,
            'robot_address': self.robot_address,
            'os_version': self.os_version,
        }

    @classmethod
    def from_dict(cls, d):
        d.pop('_id')
        location = d.pop('location')
        d['location'] = None
        capacity = cls(**d)
        capacity.location = Location(**location)
        return capacity

    def __repr__(self):
        return str(self.to_dict())


class Location():
    """
    Location of a node
    """

    def __init__(self, continent, country, city, latitude, longitude):
        self.continent = continent
        self.country = country
        self.city = city
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            'continent': self.continent,
            'country': self.country,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    def __repr__(self):
        return str(self.to_dict())


class Farmer():

    """
    Represent a threefold Farmer
    """

    def __init__(self, id, name, iyo_account, wallet_addresses=None):
        self.id = id
        self.name = name
        self.iyo_account = iyo_account
        self.wallet_addresses = wallet_addresses or []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'iyo_account': self.iyo_account,
            'wallet_addresses': self.wallet_addresses,
        }

    @classmethod
    def from_dict(cls, f):
        return cls(**f)

    def __repr__(self):
        return str(self.to_dict())


class FarmerNotFoundError(KeyError):
    pass


class NodeNotFoundError(KeyError):
    pass
