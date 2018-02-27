from js9 import j

TEMPLATE = """
redisconfigname = ""
"""


JSConfigBase = j.tools.configmanager.base_class_config


class CoreDNSClient(JSConfigBase):
    """
    info about plugin redis: 
        https://coredns.io/explugins/redis/
    """

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE,  interactive=interactive)
        self._redis = None

    @property
    def redis_config(self):
        """
        redis which is the connection to the redis backend of coredns
        """
        if self._redis is None:
            self._redis = j.clients.redis_config.get(
                instance=self.config.data["redisconfigname"])
        return self._redis

    @property
    def redis(self):
        """
        redis which is the connection to the redis backend of coredns
        """
        return self.redis_config.redis

    def _get_parts(self,dns):
        hostname = dns.split(".")[-1]
        domain = ".".join(dns.split(".")[:-1])
        return domain,hostname
        

    def record_a_set(self, dns, ipaddress):
        """
        e.g. dns = test.a.grid.tf specify the full name
        """
        self.logger.debug("write dns: %s:%s"%(dns,ipaddress))
        domain,hostname=self._get_parts(dns)
        a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        
        self.redis.hset(domain, hostname, a_record)

    def record_cname_set(self, dns, dns_cname):
        """
        e.g. dns = test.a.grid.tf specify the full name
        """
        self.logger.debug("write record_cname_set: %s:%s"%(dns,dns_cname))
        domain,hostname=self._get_parts(dns)
        raise RuntimeError("TODO:*1")
        # a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        self.redis.hset(domain, hostname, a_record)

    def record_ns_set(self, dns, dns_ns):
        """
        e.g. dns = test.a.grid.tf specify the full name
        """
        self.logger.debug("write record_cname_set: %s:%s"%(dns,dns_cname))
        domain,hostname=self._get_parts(dns)
        raise RuntimeError("TODO:*1")
        # a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        self.redis.hset(domain, hostname, a_record)


    def record_txt_set(self, dns, text):
        """
        e.g. dns = test.a.grid.tf specify the full name
        """
        self.logger.debug("write record_cname_set: %s:%s"%(dns,dns_cname))
        domain,hostname=self._get_parts(dns)
        raise RuntimeError("TODO:*1")
        # a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        self.redis.hset(domain, hostname, a_record)

    def record_mx_set(self, dns, servers):
        """
        e.g. dns = test.a.grid.tf specify the full name
        @PARAM servers = mx1.example.com:10,mx2.example.com:20
        """
        self.logger.debug("write record_cname_set: %s:%s"%(dns,dns_cname))
        domain,hostname=self._get_parts(dns)
        raise RuntimeError("TODO:*1")
        # a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        self.redis.hset(domain, hostname, a_record)

    def record_srv_set(self, dns, ...):
        """
        e.g. dns = test.a.grid.tf specify the full name
        @PARAM servers = mx1.example.com:10,mx2.example.com:20
        """
        self.logger.debug("write record_cname_set: %s:%s"%(dns,dns_cname))
        domain,hostname=self._get_parts(dns)
        raise RuntimeError("TODO:*1")
        # a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        self.redis.hset(domain, hostname, a_record)

    def record_soa_set(self, dns, ...):
        """
        e.g. dns = test.a.grid.tf specify the full name
        @PARAM servers = mx1.example.com:10,mx2.example.com:20
        """
        self.logger.debug("write record_cname_set: %s:%s"%(dns,dns_cname))
        domain,hostname=self._get_parts(dns)
        raise RuntimeError("TODO:*1")
        # a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % ipaddress
        self.redis.hset(domain, hostname, a_record)        

    def __str__(self):
        return "coredns:%-14s %-25s:%-4s" % (self.instance, self.redis_config.config.data["addr"],  self.redis_config.config.data["port"])

    __repr__ = __str__
