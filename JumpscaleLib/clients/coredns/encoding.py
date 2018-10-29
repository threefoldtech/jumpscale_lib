from urllib.parse import urlparse

def encode_record(zone):
    # Set the backend servers
    
    domain_parts = zone.domain.split('.')
    # The key for coredns should start with path(/hosts) and the domain reversed
    # i.e. test.com => /hosts/com/test
    key = "/hosts/{}".format("/".join(domain_parts[::-1]))
    value = str(zone.rrdata)
    return key,value

def unregister_record(zone):

    domain_parts = zone.domain.split('.')
    # The key for coredns should start with path(/hosts) and the domain reversed
    # i.e. test.com => /hosts/com/test
    key = "/hosts/{}".format("/".join(domain_parts[::-1]))
    return key

def load(client):
    res = []
    for value, key in client.api.get_prefix('/hosts'):
        ss = key.key.decode().split('/')
        domain = '.'.join(reversed(ss[2:]))
        res.append((domain, value))
    return res