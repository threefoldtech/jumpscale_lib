from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField,
                         FloatField, ListField, PointField,
                         ReferenceField, StringField)


class NodeRegistration:
    @staticmethod
    def list(country=None):
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

    @staticmethod
    def get(node_id):
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

    @staticmethod
    def search(country=None, mru=None, cru=None, hru=None, sru=None):
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
        query = {}
        if country:
            query['location__country'] = country
        if mru:
            query['mru__gte'] = mru
        if cru:
            query['cru__gte'] = cru
        if hru:
            query['hru__gte'] = hru
        if sru:
            query['sru__gte'] = sru
        for cap in Capacity.objects(**query):
            yield cap

    @staticmethod
    def all_countries():
        """
        yield all the country present in the database

        :return: sequence of country
        :rtype: sequence of string
        """
        countries = Capacity.objects.only('location__country')
        for cap in countries:
            yield cap.location.country


class FarmerRegistration:

    @staticmethod
    def create(self, name, iyo_account, wallet_addresses=None):
        return Farmer(name=name, iyo_account=iyo_account, wallet_addresses=wallet_addresses)

    @staticmethod
    def register(self, farmer):
        if not isinstance(farmer, Farmer):
            raise TypeError("farmer need to be a Farmer object, not %s" % type(farmer))
        farmer.save()

    @staticmethod
    def list(self):
        for farmer in Farmer.objects():
            yield farmer

    @staticmethod
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
    longitude = FloatField()
    latitude = FloatField()


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
