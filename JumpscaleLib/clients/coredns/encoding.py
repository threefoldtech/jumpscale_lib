from urllib.parse import urlparse
from ipaddress import IPv4Address, IPv6Address
from ipaddress import AddressValueError, NetmaskValueError
import json
from .ResourceRecord import ResourceRecord

def encode_record(zone):
    """encode zone record 
    
    Arguments:
        zone : ResourceRecord object that needs to be encoded
    """
    domain_parts = zone.domain.split('.')
    # The key for coredns should start with path(/hosts) and the domain reversed
    # i.e. test.com => /hosts/com/test
    key = "/hosts/{}".format("/".join(domain_parts[::-1]))
    return key,zone.rrdata

def unregister_record(zone):
    """return encoded key of zone record that needs to be deleted 
    Arguments:
        zone : ResourceRecord object that needs to be encoded
    """
    domain_parts = zone.domain.split('.')
    # The key for coredns should start with path(/hosts) and the domain reversed
    # i.e. test.com => /hosts/com/test
    key = "/hosts/{}".format("/".join(domain_parts[::-1]))
    return key

def load(client):
    """get all zones from etcd
    
    Arguments:
        client : ETCD client
    """
    zones = []
    for value, key in client.api.get_prefix('/hosts'):
        ss = key.key.decode().split('/')
        domain = '.'.join(reversed(ss[2:]))
        value = json.loads(value.decode())
        type_of_record , rrdata = get_type_and_rdata(value)
        if type_of_record == "SRV":
            zone = ResourceRecord(domain,rrdata,type_of_record,value["ttl"],value["priority"],value["port"])
        else:
            zone = ResourceRecord(domain,rrdata,type_of_record,value["ttl"])
        zones.append(zone)
    return zones

def get_type_and_rdata(record):
    """get type and data of record
    
    Arguments:
        record: dict value of zone

    Returns: type and data of type
    """
    if "text" in record:
        return 'TXT', record['text']
    elif "port" in record:
        return 'SRV', record['host']
    elif "cname" in record:
        return 'CNAME', record['cname']
    elif "host" in record:
        rrdata = record['host']
        try:
            IPv6Address(rrdata)
            rtype = 'AAAA'
            return rtype, rrdata
        except (AddressValueError, NetmaskValueError):
            try:
                IPv4Address(rrdata)
                rtype = 'A'
                return rtype, rrdata
            except (AddressValueError, NetmaskValueError):
                pass
    raise KeyError("cannot identify record type %s" % repr(record))
