
from js9 import j

JSBASE = j.application.jsbase_get_class()
from .GeventActor import GeventActor

class GeventRobot(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)
        self.servers = {}
        self.actors = {}

    def _key_get(self,name,instance):
        key="%s_%s"%(name.lower().strip(),instance.lower().strip())
        return key

    def actor_get(self,name,instance):
        key=self._get_get(name,instance)
        if key not in self.actors:
            self.actors[key] = GeventActor(name,instance)
        return self.actors[key]

    def server_add(self,name,server):
        self.servers[name]=server

    def server_start(self):
        #TODO:*1
        started = []
        try:
            for server in self.servers[:]:
                server.start()
                started.append(server)
                name = getattr(server, 'name', None) or server.__class__.__name__ or 'Server'
                self.logger.info('%s started on %s', name, server.address)
        except:
            self.stop(started)
            raise

    def server_stop(self, servers=None):
        if servers is None:
            servers = self.servers[:]
        for server in servers:
            try:
                server.stop()
            except:
                if hasattr(server, 'loop'): # gevent >= 1.0
                    server.loop.handle_error(server.stop, *sys.exc_info())
                else: # gevent <= 0.13
                    import traceback
                    traceback.print_exc()


