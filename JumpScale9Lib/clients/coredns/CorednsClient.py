from js9 import j
import json

JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
address = ""
domain_name = ""
redis_port = 6379
redis_password_ = ""
"""

class CorednsClient(JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        self.address = c['address']
        self.domain_name = c['domain_name']
        if not self.domain_name.endswith('.'):
            self.domain_name = self.domain_name + '.'
        self.redis_port = c['redis_port']
        self.redis_password = c['redis_password_']
        self._redis_client = None

    @property
    def redis_client(self):
        if not self._redis_client:
            self._redis_client = j.clients.redis.get(self.address, self.redis_port, self.redis_password)
        return self._redis_client

    def _add_record(self, subdomain, record, override=False):
        exist = self.redis_client.hget(self.domain_name, subdomain)

        if not exist or override:
            self.redis_client.hset(self.domain_name, subdomain, record)

    def register_a_record(self, subdomain, ip4, ttl=360, override=False):
        record = {
            "a":[{
                "ip": ip4,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)

    def register_aaaa_record(self, subdomain, ip6, ttl=360, override=False):
        record ={
            "aaaa":[{
                "ip": ip6,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)

    def register_cname_record(self, subdomain, host, ttl=360, override=False):
        record ={
            "cname":[{
                "host": host,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)

    def register_ns_record(self, subdomain, host, ttl=360, override=False):
        record ={
            "ns":[{
                "host": host,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)
    
    def register_text_record(self, subdomain, text, ttl=360, override=False):
        record ={
            "text":[{
                "host": text,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)
    
    def register_mx_record(self, subdomain, host, preference, ttl=360, override=False):
        record ={
            "mx":[{
                "host": host,
                "preference": preference,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)
    
    def register_srv_record(self, subdomain, priority, weight, port, target, ttl=360, override=False):
        record ={
            "srv":[{
                "priority": priority,
                "weight": weight,
                "port": port,
                "target": target,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)
    
    def register_soa_record(self, subdomain, ns, mbox, refresh, retry, expire, minttl, ttl=360, override=False):
        record ={
            "soa":[{
                "ns": ns,
                "MBox": mbox,
                "refresh": refresh,
                "retry": retry,
                "expire": expire,
                "ttl": ttl
            }]
        }
        self._add_record(subdomain, json.dumps(record), override=override)
    
    def unregister(self, *subdomains):
        self.redis_client.hdel(self.domain_name, *subdomains)