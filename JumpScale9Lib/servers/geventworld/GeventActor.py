from js9 import j

JSBASE = j.application.jsbase_get_class()

class GeventActor(JSBASE):

    def __init__(self,sessionid=0):
        JSBASE.__init__(self)
        self.sessionid = sessionid
        self.q_out = gevent.queue.Queue() #to browser
        self.q_in = gevent.queue.Queue()  #from browser
        self.greenlet = spawn(self.main)

    def main(self):
        #make sure communication is only 1 way
        while True:
            task,data=self.q_in.get()
            self.q_out.put(self.__dict__(task)(data))

    def task1(self,id):
        return id+1

    def task2(self,id):
        return "task2:%s"%id
