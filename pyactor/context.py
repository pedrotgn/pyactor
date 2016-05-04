from urlparse import urlparse
from actor import Actor,ActorRef
from proxy import Proxy
from util import *
import signal, sys
from time import sleep
import threading

def create_host(url='local://local:6666/host'):
    global host
    if host[0]:
        raise Exception('Host already created. Only one host can be ran at a time.')
    else:
        host[0] = Host(url)
        return host[0]

class Host(object):
    '''
    Host is the container of the actors. It manages the spawn and elimination of
    actors and their communication through channels. Also configures the TCP socket
    where the actors will be able to recieve queries remotely.
    '''
    _tell = []
    _ask = ['spawn','lookup','spawn_n','lookup_url']

    def __init__(self,url):
        self.actors = {}
        self.threads = {}
        self.url = url
        self.online = False
        self.load_transport(url)
        self.init_host()

    def load_transport(self, url):
        '''
        For TCP communication. Sets the communication socket of the host at the
        address and port specified.

        :param str. url: URL where to bind the host. Must be provided in the
            tipical format: 'scheme://address:port/hierarchical_path'
        '''
        aurl = urlparse(url)
        addrl = aurl.netloc.split(':')
        self.addr = addrl[0],addrl[1]
        self.transport = aurl.scheme
        self.host_url = aurl

        '''
        if aurl.scheme == 'tcp':
            self.tcp = Server(self.addr)
            dispatcher = self.tcp.get_dispatcher(self.addr)
            launch_actor(self.addr,dispatcher)'''

            #self.aref = 'atom://' + self.dispatcher.name + '/controller/Host/0'
            #self.name = self.dispatcher.name

    def spawn(self,id,klass,args=[]):
        '''
        This sync method creates an actor attached to this host. It will be an
        instance of the class *klass* and it will be assigned an ID that identifies
        it among the host.

        :param str. id: identifier for the spawning actor. Unique within the host.
        :param class klass: class type of the spawning actor.
        :param list args: arguments for the init function of the spawning actor class.
        :return: :class:`~.Proxy` of the actor spawned.
        :raises: :class:`AlreadyExists`, if the ID specified is already in use.
        '''
        url = '%s://%s/%s' % (self.transport,self.host_url.netloc,id)
        if self.actors.has_key(url):
            raise AlreadyExists()
        else:
            obj = klass(*args)
            obj.id = str(id)
            new_actor = Actor(url,klass,obj)
            obj.proxy = Proxy(new_actor)
            if self.online:
                obj.host = self.proxy
            else:
                obj.host = Exception("Host is not an active actor. Use 'init_host' to make it alive.")
            self.launch_actor(url,new_actor)
            return Proxy(new_actor)


    def spawn_n(self,n,id,klass,args=[]):
        '''Sync method.
        Spwns n actors at a time as a group. All the actors will have the same
        ID and channel. All the communications will proceed to all the actors of
        the grup at a time.

        :param int n: Number of actors to spawn in the group.
        :param str. id: identifier for this actors; must be unique within the
            other actors of the host.
        :param class klass: class type of the actors to be spawned.
        :param list args: arguments to the init function of the class  *klass*.
        :return: :class:`~.Proxy` of one of the actors, which will also
            communicate whit all the others.
        :raises: :class:`AlreadyExists`, if the ID specified is already in use.
        '''
        url = '%s://%s/%s' % (self.transport,self.host_url.netloc,id)
        if self.actors.has_key(url):
            raise AlreadyExists()
        else:
            group  = [Actor(url,klass,args,id) for i in range(n)]
            for elem in group[1:]:
                elem.channel = group[0].channel
            for new_actor in group:
                self.launch_actor(url,new_actor)
            return Proxy(new_actor)

    def lookup(self,id):
        '''Sync method.
        Gets a new proxy that references to the actor of the host identified by
        the given ID.

        :param str. id: identifier of the actor you want.
        :return: :class:`~.Proxy` of the actor requiered.
        '''
        url =  '%s://%s/%s' % (self.transport,self.host_url.netloc,id)
        if self.actors.has_key(url):
            return Proxy(self.actors[url])
        else:
            raise NotFound()

    def shutdown(self):
        '''Async method.
        Stops the Host, stopping at the same time all its actors.
        Should be called at the end of its usage, to finish correctly all the
        connections.
        When the actors stop running, they can't be started again.

        '''
        for actor in self.actors.values():
            if actor.id != self.id:
                Proxy(actor).stop()
                actor.thread.join()

        self.actors.clear()
        self.online=False
        host[0] = None



    def lookup_url(self, url,klass):
        '''Sync method.
        Gets a proxy reference to the actor indicated by the URL in the parameters.
        It can be a local reference or a TCP direction.

        :param srt. url: address that identifies an actor.
        :param class klass: class type of the actor to lookup.
        :return: :class:`~.Proxy` of the actor requested.
        :raise: :class:`NotFound`, if the URL specified do not correspond to any
            actor in the host.
        '''
        aurl = urlparse(url)
        if self.is_local(aurl):
            if not self.actors.has_key(url):
                raise NotFound()
            else:
                return Proxy(self.actors[url])
        else:
            raise Exception("TCPthing")
            '''addrl = aurl.netloc.split(':')
            addr = addrl[0],addrl[1]
            if actors.has_key(addr):
                dispatcher = actors[addr]
            else:
                dispatcher = self.tcp.get_dispatcher(addr)
                launch_actor(addr,dispatcher)
            remote_actor = ActorRef(url,klass,dispatcher.channel)
            return Proxy(remote_actor)'''


    def is_local(self,aurl):
        '''Sync method.
        Tells if the address given is from this host.

        :param ParseResult aurl: address to analyze.
        :return: (*Bool.*) If is local (**True**) or not (**False**).
        '''
        return self.host_url.netloc == aurl.netloc


    def launch_actor(self, url,actor):
        '''
        This function makes an actor alive to start processing queries.

        :param str. url: identifier of the actor.
        :param Actor actor: instance of the actor.
        '''
        actor.run()
        self.actors[url] = actor
        self.threads[actor.thread] = url


    def init_host(self):
        '''
        This is the main function to create a new Host to which you can spawn actors.
        It will be set by default at local address if no parameter *url* is given.

        :param str. url: URL where to start and bind the host.
        :return: :class:`~.Proxy` of the host.
        '''
        self.id = self.url
        host = Actor(self.url,Host,self)
        self.proxy = Proxy(host)
        self.launch_actor(self.url,host)
        self.online = True



    def signal_handler(self, signal, frame):
        '''
        This gets the signal of Ctrl+C and stops the host. It also ends the execution.

        :param signal: SIGINT signal interruption sent with a Ctrl+C.
        :param frame: the current stack frame. (not used)
        '''
        print 'You pressed Ctrl+C!'
        self.shutdown()

        #sys.exit(0)


    def serve_forever(self):
        '''
        This allows the host to keep alive indefinitely so its actors can receive
        queries at any time.
        To kill the execution, press Ctrl+C.

        See usage example in :ref:`sample5`.
        '''
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        print 'Press Ctrl+C to kill the execution'
        while self.running:
            sleep(1)
        print 'BYE!'
