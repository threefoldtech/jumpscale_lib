import requests

from js9 import j
from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField,
                         FloatField, IntField, ListField, PointField,
                         ReferenceField, StringField, connect)


class CapacityRegistration:

    def __init__(self):
        # TODO: need to hardcode location of the mongodb cluster for tf capacity
        connect(db='capacity', host='localhost', port=27017)
        self.nodes = NodeRegistration()
        self.farmer = FarmerRegistration()


class NodeRegistration:

    # def __init__(self):
    #     # self._nodes = nodes  # mongodb collection

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
                    geolocation=[data.get('location').get('longitude'), data.get('location').get('latitude')]
                )

        capacity.save()

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
            filter['location__country'] = country

        for capacity in Capacity.objects(**filter):
            yield capacity

    def get(self, node_id):
        """
        return the capacity for a single node

        :param node_id: unique node ID
        :type node_id: str
        :return: Capacity object
        :rtype: Capacity
        """
        capacity = Capacity.objects(pk=node_id)
        if not capacity:
            raise NodeNotFoundError("node '%s' not found" % node_id)
        return capacity[0]

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
            filter['location__country'] = country
        if mru:
            filter['mru__gte'] = mru
        if cru:
            filter['cru__gte'] = cru
        if hru:
            filter['hru__gte'] = hru
        if sru:
            filter['sru__gte'] = sru
        print(filter)
        for cap in Capacity.objects(**filter):
            yield cap

    def all_countries(self):
        """
        yield all the country present in the database

        :return: sequence of country
        :rtype: sequence of string
        """
        countries = Capacity.objects.only('location__country')
        for cap in countries:
            yield cap.location.country


class FarmerRegistration:

    def create(self, name, iyo_account, wallet_addresses=None):
        return Farmer(name=name, iyo_account=iyo_account, wallet_addresses=wallet_addresses)

    def register(self, farmer):
        if not isinstance(farmer, Farmer):
            raise TypeError("farmer need to be a Farmer object, not %s" % type(farmer))
        farmer.save()

    def list(self):
        for farmer in Farmer.objects():
            yield farmer

    def get(self, id):
        farmer = Farmer.objects(pk=id)
        if not farmer:
            raise FarmerNotFoundError("farmer '%s' not found" % id)
        return farmer[0]


class Location(EmbeddedDocument):
    """
    Location of a node
    """
    continent = StringField()
    country = StringField()
    city = StringField()
    geolocation = PointField()


class Farmer(Document):

    """
    Represent a threefold Farmer
    """
    # id = StringField(primary_key=True)
    name = StringField()
    iyo_account = StringField()
    wallet_addresses = ListField(StringField())


class Capacity(Document):
    """
    Represent the ressource units of a zero-os node
    """
    node_id = StringField(primary_key=True)
    location = EmbeddedDocumentField(Location)
    farmer = ReferenceField(Farmer)
    cru = FloatField()
    mru = FloatField()
    hru = FloatField()
    sru = FloatField()
    robot_address = StringField()
    os_version = StringField()


class FarmerNotFoundError(KeyError):
    pass


class NodeNotFoundError(KeyError):
    pass
