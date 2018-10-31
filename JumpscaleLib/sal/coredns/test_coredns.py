from .encoding import load,encode_record,unregister_record,get_type_and_rdata
from .CoreDnsClient import CoreDnsClient
from .ResourceRecord import ResourceRecord

class Meta:

    def __init__(self, key):
        self.key = key


class Api:
    def __init__(self, client):
        self._client = client

    def get(self, key):
        if isinstance(key, str):
            key = key.encode()
        value = self._client._data.get(key)
        return (value, Meta(key))

    def get_prefix(self, prefix):
        if isinstance(prefix, str):
            prefix = prefix.encode()
        for k, v in list(self._client._data.items()):
            if k.startswith(prefix):
                yield (v, Meta(k))

    def delete_prefix(self, prefix):
        if isinstance(prefix, str):
            prefix = prefix.encode()
        for k in list(self._client._data.keys()):
            if k.startswith(prefix):
                del self._client._data[k]


class EtcdClientMock:
    def __init__(self):
        self._data = {}
        self.api = Api(self)

    def put(self, key, value):
        if isinstance(value, str):
            value = value.encode()
        self._data[key.encode()] = value

    def get(self, key):
        return self._data.get(key)


def test_zone_deploy_remove():
    client = EtcdClientMock()
    zone1 = ResourceRecord('test1.example.com','10.144.13.199',record_type='A')
    key, value = encode_record(zone1)
    client.put(key, value)
    zone2 = ResourceRecord('test2.example.com','2003::8:1',record_type='AAAA')
    key, value = encode_record(zone2)
    client.put(key, value)

    assert client._data == {
        b'/hosts/com/example/test1': b'{"ttl": 300, "host": "10.144.13.199"}',
        b'/hosts/com/example/test2': b'{"ttl": 300, "host": "2003::8:1"}',
    }

    key = unregister_record(zone1)
    client.api.delete_prefix(key)
    key = unregister_record(zone2)
    client.api.delete_prefix(key)
    assert client._data == {}

def test_encoding_zone():
    client = EtcdClientMock()
    zone1 = ResourceRecord('test1.example.com','10.144.13.199',record_type='A')
    key, value = encode_record(zone1)
    client.put(key, value)
    zone2 = ResourceRecord('test2.example.com','2003::8:1',record_type='AAAA')
    key, value = encode_record(zone2)
    client.put(key, value)

    assert client._data == {
        b'/hosts/com/example/test1': b'{"ttl": 300, "host": "10.144.13.199"}',
        b'/hosts/com/example/test2': b'{"ttl": 300, "host": "2003::8:1"}',
    }

def test_backend_load():
    client = EtcdClientMock()
    client._data = {
        b'/hosts/com/example/test1': b'{"ttl": 300, "host": "10.144.13.199"}',
        b'/hosts/com/example/test2': b'{"ttl": 300, "host": "2003::8:1"}',
    }
    zones = load(client)
    print(zones[0].rrdata)
    assert zones[0].domain == "test1.example.com"
    assert zones[0].rrdata == '{"ttl": 300, "host": "10.144.13.199"}'
    assert zones[0].ttl == 300
    assert zones[1].domain == 'test2.example.com'
    assert zones[1].rrdata == '{"ttl": 300, "host": "2003::8:1"}'
    assert zones[1].ttl == 300

def test_type_and_rdata():
    type_of_record, metadata = get_type_and_rdata({"ttl": 300, "host": "10.144.13.199"})
    assert type_of_record == "A"
    assert metadata == "10.144.13.199"
    type_of_record, metadata = get_type_and_rdata({"ttl": 300, "host": "2003::8:1"})
    assert type_of_record == "AAAA"
    assert metadata == "2003::8:1"