from js9 import j

from pprint import pprint as print
from .OVCClient import OVCClient

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class OVCClientFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"
        self.logger = j.logger.get("OVC Client Factory")
        self.__imports__ = "ovc"
        JSConfigBaseFactory.__init__(self, OVCClient)

    # TODO:*1 change ays to use the config mgmt, in any class where you need e.g. the client just do j.clients.openvcloud.get(instance=...)
    # the instance name is only thing which needs to be in the relevan AYS

    def getFromAYSService(self, service):
        """
        Returns an OpenvCloud Client object for a given AYS service object.
        """
        data = {'address': service.model['data'].get('url'),
                'login': service.model['data'].get('login', ""),
                'JWT_': service.model['data'].get('jwt'),
                'port': service.model['data'].get('port')}
        # toml = j.data.serializer.toml.dumps(data)
        return self.get(data=data)

    def get_for_operator(self, instance="main", data={}):
        """
        this will return a client always created for the operator even if the appkey has been filled in
        """
        i = self.get(instance, data)
        i.operator = True
        return i

    def get_for_enduser(self, instance="main", data={}):
        """
        this will return a client always created for the enduser
        """
        i = self.get(instance, data)
        i.operator = False
        return i

    def test(self):

        def mytest_as_operator():

            cl = self.get_for_operator()
            print(cl.config)

            print("locations")
            print(cl.locations)

            print("images")
            print(cl.get_available_images())

        def mytest_as_enduser():

            cl = self.get_for_enduser()

            print("images")
            print(cl.get_available_images())

        # mytest_as_enduser() #TODO:*1 not working yet, needs to be done
        mytest_as_operator()
