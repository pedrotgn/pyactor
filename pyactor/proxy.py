from actor import Channel
from util import *
from Queue import Empty

class Proxy:
    def __init__(self, actor):
        self.__channel = actor.channel
        self.actor = actor
        for method in actor.tell:
            setattr(self, method, TellWrapper(self.__channel,method,actor.url))
        for method in actor.ask:
            setattr(self, method, AskWrapper(self.__channel,method,actor.url))

    def __repr__(self):
        return 'Proxy(actor=%s, tell=%s, ask = %s)' % (self.actor, self.actor.tell,self.actor.ask)




class Future(object):
    def __init__(self,actor_channel,method,params,actor_url):
        self.__channel = Channel()
        self.__method = method
        self.__params = params
        self.__actor_channel = actor_channel
        self.__target = actor_url

    def get(self,timeout=1):
        #_from  = get_current()
        ##  SENDING MESSAGE ASK
        #msg = (_from, self.target,ASK, self.method,self.params, self.channel)
        msg = AskRequest(ASK,self.__method,self.__params,self.__channel,self.__target)
        self.__actor_channel.send(msg)
        try:
            response = self.__channel.receive(timeout)
            result = response.result
            if isinstance(result, Exception):
                raise result
            else:
                return result
        except Empty,e:
            raise Timeout()

    def add_callback(self,callback):
        _from = get_current()
        from_actor = actors[_from]
        ##  SENDING MESSAGE FUTURE
        #msg = (_from, self.target, FUTURE, self.method,self.params,callback,actors[_from].channel)
        msg = FutureRequest(FUTURE,self.__method,self.__params,callback,from_actor.channel,self.__target,from_actor.url)
        self.__actor_channel.send(msg)



class TellWrapper:
    def __init__(self, channel, method, actor_url):
        self.__channel = channel
        self.__method = method
        self.__target = actor_url

    def __call__(self, *args, **kwargs):
        #_from = get_current()
        ##  SENDING MESSAGE TELL
        #msg = (_from, self.__target, TELL, self.__method,args)
        msg = TellRequest(TELL,self.__method,args,self.__target)
        self.__channel.send(msg)

class AskWrapper:
    def __init__(self, channel, method,actor_url):
        self.__channel = channel
        self.__method = method
        self.target = actor_url

    def __call__(self, *args, **kwargs):
        return Future(self.__channel,self.__method,args, self.target)
