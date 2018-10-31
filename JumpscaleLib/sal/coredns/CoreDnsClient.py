from jumpscale import j
import json
from .encoding import (encode_record,unregister_record,load)
from .ResourceRecord import ResourceRecord ,RecordType
JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
etcd_instance = "main"
"""
class CoreDnsClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self._etcd_client = None
        print ("CoreDNS", instance)
        self._zones = []


    @property
    def etcd_client(self):
        if not self._etcd_client:
            self._etcd_client = j.clients.etcd.get(self.config.data['etcd_instance'])
        return self._etcd_client

    @property
    def zones(self):
        """get all zones 
        """
        if not self._zones:
            self._zones = load(self.etcd_client)
        return self._zones

    def zone_create(self, domain, rrdata, record_type=RecordType.A,  ttl=300, priority=None, port=None ):
        """ create new zone .

            domain    : Record Name.  Corresponds to first field in
                      DNS Bind Zone file entries.  REQUIRED.
            rrdata  : Resource Record Data (REQUIRED)
            record_type    : Record Type.  CNAME, A, AAAA, TXT, SRV.  REQUIRED
            ttl     : time to live. default value 300 (optional)
            priority: SRV record priority (optional)
            port    : SRV record port (optional)

            TXT record example  : rrdata = 'this is a TXT record'
            A record example    : rrdata = '1.1.1.1'
            AAAA record example : rrdata = '2003:8:1'
            SRV record example  : rrdata = 'skydns-local.server'
            CNAME record example: rrdata = 'cn1.skydns.local skydns.local.'
        """
        zone = ResourceRecord(domain, rrdata, record_type, ttl, priority, port)
        self._zones.append(zone)
        return zone

    def deploy(self):
        """
        add coredns records in etcd
        :param zones: list of `ResourceRecord` objects that needs to be added
        """
        for zone in self.zones:
            key, value = encode_record(zone)
            self.etcd_client.put(key, value)
    
    def remove(self, zones):
        """
        remove coredns records from etcd
        :param zones: list of `ResourceRecord` objects that needs to be removed
        """
        for zone in zones:
            key = unregister_record(zone)
            self.etcd_client.api.delete_prefix(key)

    def zone_exists(self, domain, record_type=RecordType.A ):
        """
        search of zone in zones list
        
        Arguments:
            domain {string} 
        
        Keyword Arguments:
            record_type {enum} (default: {RecordType.A})
        
        Returns:
            true if exist
        """
        for zone in self.zones:
            if zone.domain == domain and zone.type == record_type:
                return True
        return False
