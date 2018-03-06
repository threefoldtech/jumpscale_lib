from __future__ import print_function
from js9 import j


import dns
import dns.message
import dns.rdataclass
import dns.rdatatype
import dns.query
import dns.resolver

JSBASE = j.application.jsbase_get_class()


class DNSTools(JSBASE):
    """
    to install:
    pip3 install dnspython
    """


    def __init__(self):
        self.__jslocation__ = "j.tools.dnstools"
        JSBASE.__init__(self)

    def getNameserversForDomain(self,domain="threefoldtoken.org",nameserver="8.8.8.8"):

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [nameserver]
        answer = dns.resolver.query(domain, 'NS')

        res=[]
        for rr in answer:
            res.append( rr.target.to_text())
        return res

    def getNameRecordIPs(self,dnsurl="www.threefoldtoken.org",nameserver="8.8.8.8"):
        """
        return ip addr for a full name
        """

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [nameserver]
        answer = dns.resolver.query(dnsurl, 'A')

        res=[]
        for rr in answer:
            res.append( rr.address)
        return res