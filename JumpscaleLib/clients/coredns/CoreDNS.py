from Jumpscale import j
import json
from .encoding import (encode_record,unregister_record,load)
from enum import Enum
JSConfigBase = j.tools.configmanager.JSBaseClassConfig

TEMPLATE = """
etcd_instance = "main"
secrets_ = ""
"""

class RecordType(Enum):
    A = "A"
    AAAA = "AAAA"
    SRV = "SRV"
    TXT = "TXT"

class ResourceRecord:

    def __init__(self, domain, rrdata, record_type=RecordType.A,  ttl=300,
                             priority=None, port=None # SRV
                ):
        """ DNS Resource Record.

            name    : Record Name.  Corresponds to first field in
                      DNS Bind Zone file entries.  REQUIRED.
            record_type    : Record Type.  CNAME, A, AAAA, TXT, SRV.  REQUIRED
            ttl     : time to live. default value 300 (optional)
            port    : SRV record port (optional)
            priority: SRV record priority (optional)
            rrdata  : Resource Record Data (REQUIRED)

            TXT record example  : rrdata = 'this is a TXT record'
            A record example    : rrdata = '1.1.1.1'
            AAAA record example : rrdata = '2003:8:1'
            SRV record example  : rrdata = 'skydns-local.server'
            CNAME record example: rrdata = 'cn1.skydns.local skydns.local.'
        """

        if rrdata is None:
            rrdata = ''

        self.type = record_type
        if self.type == 'CNAME':
            self.cname, rrdata = rrdata.split(' ')
        self.domain = domain
        self.port = port
        self.priority = priority
        self.ttl = ttl
        self.weight = 100
        self._rrdata = rrdata


    @property
    def rrdata(self):
        """ reconstructs CoreDNS/etcd-style JSON data format
        """
        res = {'ttl': self.ttl}
        rdatafield = 'host' # covers SRV, A, AAAA and CNAME
        if self.type == RecordType.TXT:
            rdatafield = 'text'
        elif self.type == RecordType.SRV:
            res['priority'] = self.priority
            res['port'] = self.port
        elif self.type == 'CNAME':
            res['cname'] = self._rrdata # hmmm... weird, these being inverted
            res['host'] = self.cname    # weeeeird....
        res[rdatafield] = self._rrdata
        return res

    def __str__(self):
        if self.type == 'TXT':
            rrdata = '"%s"' % self._rrdata
        else:
            rrdata = self._rrdata
        extra = 'IN\t%s' % self.type
        if self.type == 'SRV':
            extra += '\t%d %d %d' % (self.priority, self.weight, self.port)
        return "%s\t%d\t%s\t%s" % \
            (self.domain, self.ttl, extra, rrdata)

    def __repr__(self):
            return "'%s'" % str(self)

class CoreDNS(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self._etcd_client = None
        self._etcd_instance = self.config.data['etcd_instance']
        print ("CoreDNS", instance)
        self.zones = []

    @property
    def secrets(self):
        res={}
        if "," in self.config.data["secrets_"]:
            items = self.config.data["secrets_"].split(",")
            for item in items:
                if item.strip()=="":
                    continue
                nsname,secret = item.split(":")
                res[nsname.lower().strip()]=secret.strip()
        else:
            res["default"]=self.config.data["secrets_"].strip()
        return res

    @property
    def etcd_client(self):
        if not self._etcd_client:
            self._etcd_client = j.clients.etcd.get(self._etcd_instance)
        return self._etcd_client

    def zone_create(self, domain, rrdata, record_type=RecordType.A,  ttl=300,
                             priority=None, port=None ):
         
        zone =ResourceRecord(domain, rrdata, record_type, ttl, priority, port)
        self.zones.append(zone)

    def deploy(self):
        for zone in self.zones:
            key, value = encode_record(zone)
            self.etcd_client.put(key, value)
    
    def remove_record(self):
        for zone in self.zones:
            key = unregister_record(zone)
            self.etcd_client.api.delete_prefix(key)
    
    def zones_get(self):
        for domain,value in load(self.etcd_client):
            print("{}= {}".format(domain,value))