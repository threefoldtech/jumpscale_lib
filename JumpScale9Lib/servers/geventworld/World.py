
from js9 import j

JSBASE = j.application.jsbase_get_class()
import gevent
from .ActorCommunity import ActorCommunity
from .Actor import Actor
from .ServerRack import ServerRack

class Worlds(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.gworld"
        JSBASE.__init__(self)

    def community_get(self):
        return ActorCommunity()

    def server_rack_get(self):
        return ServerRack()        

    def actor_class_get(self):
        return Actor

    def test_actors(self):
        """
        js9 'j.servers.gworld.test_actors()'
        """
        community=j.servers.gworld.community_get()
        community.actor_dna_add()
        r1=community.actor_get("kristof.mailprocessor","main")
        r2=community.actor_get("kristof.mailprocessor","failback")

        for i in range(100):
            assert (0,11) == r2.action_ask("task1",10) #returns resultcode & result

        assert True == r2.monitor_running()
        assert True == r2.running()


        community.start()


    def test_servers(self,zdb_start=False):
        """
        js9 'j.servers.gworld.test_servers(zdb_start=False)'
        """
        rack=j.servers.gworld.server_rack_get()

        if zdb_start:
            cl = j.clients.zdb.testdb_server_start_client_get(start=True)  #starts & resets a zdb in seq mode with name test       

        ws_dir = j.clients.git.getContentPathFromURLorPath("https://github.com/rivine/recordchain/tree/master/apps/master")


        server = j.servers.gedis.configure(host = "localhost", port = "8000", websockets_port = "8001", ssl = False, \
            zdb_instance = "test",
            secret = "", app_dir = ws_dir, instance='test')

        redis_server,websocket_server = j.servers.gedis.geventservers_get("test")
        rack.add("gedis",redis_server)    
        rack.add("websocket",websocket_server)    

        #configure a local webserver server (the master one)
        j.servers.web.configure(instance="test", port=5050,port_ssl=0, host="localhost", secret="", ws_dir=ws_dir)

        #use jumpscale way of doing wsgi server (make sure it exists already)
        ws=j.servers.web.geventserver_get("test")
        rack.add("web",ws)

        # dnsserver=j.servers.dns.get(5355)
        # rack.add(dnsserver)

        # #simple stream server on port 1234
        # from gevent import socket
        # from gevent.server import StreamServer
        # def echo(socket, address):
        #     print('New connection')
        #     socket.sendall(b'Welcome to the echo server! Type quit to exit.\r\n')
        #     # using a makefile because we want to use readline()
        #     rfileobj = socket.makefile(mode='rb')
        #     while True:
        #         line = rfileobj.readline()
        #         if not line:
        #             print("client disconnected")
        #             break
        #         if line.strip().lower() == b'quit':
        #             print("client quit")
        #             break
        #         socket.sendall(line)
        #         print("echoed %r" % line)
        #     rfileobj.close()

        # sserver = StreamServer(('', 1234), echo,spawn=10)

        # rack.add(sserver)

        rack.start()

        gevent.sleep(1000000000)

        rack.stop()



        
