"""
zc = j.clients.zerotier.get(name="geert", data={'token_':"jkhljhbljb"})
mynetworks = zc.list_networks()-> [ZerotierNetwork]
mynetwork = zc.get_network(networkid='khgfghvhgv') -> ZerotierNetwork
zc.create_network(public=True, subnet="10.0.0.0/24", auto_assign=True, routes=[])
mymembers = mynetwork.list_members() -> [ZerotierNetworkMember]
mymember = mynetwork.get_member(address='hfivivk' || name='geert' || public_ip='...' || private_ip='...')
mymember.authorize()
mymember.deauthorize()
"""

from js9 import j

JSConfigFactory = j.tools.configmanager.base_class_configs


from .ZerotierClient import ZerotierClient


JSBASE = j.application.jsbase_get_class()



class ZerotierFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.zerotier"
        self.__imports__ = "zerotier"
        self.connections = {}
        JSConfigFactory.__init__(self, ZerotierClient)

    def test(self):
        """
        j.clients.zerotier.test()
        """
        import time

        # create a test client using a test token
        TOKEN = 'txBz8dHAyBy6tuPqhywhr9cR6ceacwWg'

        zt_client = j.clients.zerotier.get(instance='testclient', data={'token_': TOKEN})

        # make sure zerotier is installed and started
        # j.tools.prefab.local.network.zerotier.build()

        # start the daemon
        # j.tools.prefab.local.network.zerotier.start()

        # create a new test network
        network = zt_client.create_network(public=True, name='mytestnet', subnet='10.0.0.0/24')

        # try to make the the current machine join the new network
        j.tools.prefab.local.network.zerotier.join_network(network_id=network.id)
        time.sleep(20)

        # lets list the members then
        members = network.list_members()

        assert len(members) == 1, "Unexpected number of members. Expected 1 found {}".format(len(members))

        # lets try to authorize the member, shouldnt affect anything since it a public netowrk
        member = members[0]
        member.authorize()
        assert member.data['config']['authorized'] == True, "Members of public networks should be authorized"

        # now lets unauthorize, shouldnt have any effect
        member.deauthorize()
        assert member.data['config']['authorized'] == True, "Members of public networks should be authorized"

        # lets list all the networks for our current user
        networks = zt_client.list_networks()

        # lets get the network object using the network id we just created
        network = zt_client.get_network(network_id=network.id)
        assert network.name == 'mytestnet'

        # now lets delete the testnetwork we created
        zt_client.delete_network(network_id=network.id)
