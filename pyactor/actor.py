from Queue import Queue,Empty
from threading import Thread
from util import *




class Channel(Queue):
    """
    Channel is the main communication mechanism between actors. It is actually a simple facade to the
    Queue.Queue python class.
    """
    def __init__(self):
        Queue.__init__(self)

    def send(self,msg):
        #print msg
        """
        It sends a message to the current channel

        :param msg: The message sent to an actor. It is a tuple using the constants in util.py
        """
        self.put(msg)

    def receive(self, timeout = None):
        """
        It receives a message from the channel, blocking the calling thread until the response is received, or
        the timeout is triggered

        :param timeout: timeout to wait for messages. If none provided it will block until a message arrives.
        :return: returns a message sent to the channel
        """
        return self.get(timeout=timeout)

class ActorRef(object):
    def __init__(self,url,klass,channel=None):
    #channel=Channel()):
        self.url = url
        if channel:
            self.channel = channel
        else:
            self.channel = Channel()
        self.tell = klass._tell
        self.ask = klass._ask
        self.klass = klass

    def __repr__(self):
        return 'Actor(url=%s, class=%s)' % (self.url, self.klass)


class Actor(ActorRef):
    def __init__(self, url, klass, args=[]):
        super(Actor,self).__init__(url,klass)
        #self.url = url
        #self.channel = Channel()
        self.__obj = klass(*args)
        #self.__obj = klass(*args)
        #self.tell = klass._tell
        #self.ask = klass._ask
        self.tell.append('stop')
        self.running = True


    def __processQueue(self):
        while self.running:
            message = self.channel.receive()
            self.receive(message)

    def is_alive(self):
        return self.running

    def receive(self,msg):
        ''' receive messages and invokes object method'''
        if msg.method=='stop':
                self.running = False
        else:
            result = None
            try:
                invoke = getattr(self.__obj, msg.method)
                params = msg.params
                result = invoke(*params)

            except Exception, e:
                result = e
                print result
            if msg.type == ASK:
                response = AskResponse(result)
                msg.channel.send(response)
            if msg.type == FUTURE:
                response = TellRequest(TELL,msg.callback,[result],msg.from_url)
                #response = (msg[TO],msg[FROM],TELL, msg[FUTURE],[result])
                #response = TellRequest(TELL,msg.callback,[result],msg.from)
                msg.channel.send(response)


    def run(self):
        self.thread = Thread(target=self.__processQueue)
        self.thread.start()
        #threads[self.thread] = self.aref
