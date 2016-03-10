from urlparse import urlparse
from actor import Actor,ActorRef
from proxy import Proxy
from tcp import TCPDispatcher
from util import *
import signal, sys
from time import sleep


class Host(object):
    _tell = ['shutdown']
    _ask = ['spawn','lookup','spawn_n','lookup2']

    def __init__(self,name,transport):
        self.name = name
        self.load_transport(transport)

    def load_transport(self, transport):
        if transport != ():
            host,port = transport[1]
            self.dispatcher = TCPDispatcher(transport[1])
            launch_actor(transport[0],self.dispatcher)
            #self.aref = 'atom://' + self.dispatcher.name + '/controller/Host/0'
            #self.name = self.dispatcher.name

    def spawn(self,id,klass,args=[]):
        #  url = 'local://name/'+i
        if actors.has_key(id):
            raise AlreadyExists()
        else:
            new_actor = Actor(id,klass,args)
            launch_actor(id,new_actor)
            return Proxy(new_actor)


    def spawn_n(self,n,id,klass,args=[]):
      #  url = 'local://name/'+id
        if actors.has_key(id):
            raise AlreadyExists()
        else:
            group  = [Actor(id,klass,args) for i in range(n)]
            for elem in group[1:]:
                elem.channel = group[0].channel
            for new_actor in group:
                launch_actor(id,new_actor)
            return Proxy(new_actor)

    def lookup(self,id):
        if actors.has_key(id):
            return Proxy(actors[id])
        else:
            raise NotFound()

    # problem with spawn_n and sample3.py.
    def shutdown(self):
        for actor in actors.values():
            Proxy(actor).stop()


    def lookup2(self, aref,klass):
        aurl = urlparse(aref)
        print aurl
        if self.dispatcher.is_local(aurl.netloc):
            if not actors.has_key(aurl.path):
                raise NotFound(aref)
            else:
                return Proxy(actors[id])
        else:
            remote_actor = ActorRef(aref,klass,self.dispatcher.channel)
            return Proxy(remote_actor)




def launch_actor(id,actor):
    actor.run()
    actors[id] = actor
    threads[actor.thread] = id


def init_host(name='default',transport=()):
    host = Actor(name,Host,[name,transport])
    launch_actor(name,host)
    global _host
    _host = Proxy(host)
    return _host


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    _host.shutdown()
    sys.exit(0)


def serve_forever():
    signal.signal(signal.SIGINT, signal_handler)
    print 'Press Ctrl+C to kill the execution'
    while True:
        sleep(1)
