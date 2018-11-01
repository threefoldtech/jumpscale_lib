from .encoding import encode_record,get_type_and_rdata
import json


class ServiceExistError(Exception):
    pass


def zone_exists_etcd (zone, client):
    x = 1
    key,_  = encode_record(zone)
    for value, metadata in client.api.get_prefix(key):
        ss =metadata.key.decode().split('/')
        domain = '/'.join(ss[:-1])
        if key == domain:
            value = json.loads(value.decode())
            _ , rrdata = get_type_and_rdata(value)
            if rrdata != zone.rrdata:
               x = int(ss[-1][1:])
               x += 1
            else:
                raise ServiceExistError("a domain with name %s already exist. with the same value %s`" % (zone.domain, zone.rrdata))
    return x

def zone_exists_list(zone , zones):
    x = 1
    for zone_in_list in zones:
        ss=zone_in_list.domain.split('.')
        domain = '.'.join(ss[1:])
        if zone.domain == domain:
            if zone_in_list.rrdata != zone.rrdata:
                x = int(ss[0][1:])
                x += 1
            else:
                raise ServiceExistError("a domain with name %s already exist. with the same value %s`" % (zone.domain, zone.rrdata))

    return x
