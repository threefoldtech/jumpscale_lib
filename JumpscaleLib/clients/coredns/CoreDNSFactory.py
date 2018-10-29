from Jumpscale import j

from .CoreDNS import CoreDNS

JSConfigFactoryBase = j.tools.configmanager.JSBaseClassConfigs

class CoreDNSFactory(JSConfigFactoryBase):
    def __init__(self):
        self.__jslocation__ = "j.clients.coredns"
        JSConfigFactoryBase.__init__(self, CoreDNS)

    def configure(self, instance_name, host, port="2379", user="root", password="root"):
        """
        gets an instance of coredns client with etcd configurations directly
        """
        j.clients.etcd.get(instance_name, data={"host": host, "port": port, "user": user, "password_": password})
        return self.get(instance_name, data={"etcd_instance": instance_name})

    def test(self):
        #create etcd client
        cl = j.clients.coredns.configure(instance_name="main",host="10.144.72.95",password="njufdmrq3k")
        #create zones
        cl.zone_create('test.example.com','10.144.13.199',types='A')
        cl.zone_create('example.com','10.144.218.172',types='AAAA')
        #add records in etcd
        cl.add_records() 
        #get records from etcd
        cl.zones_get()
        #remove records from etcd
        cl.remove_record()
