from actor import Channel
from util import *
from Queue import Empty
from functools import wraps

class Proxy:
    '''
    Proxy is the class that supports to create a remote reference to an actor
    and invoke its methods.

    :param Actor actor: the actor the proxy will manage.
    '''
    def __init__(self, actor):
        self.__channel = actor.channel
        self.actor = actor

        for method in actor.ask_ref:
            setattr(self, method, AskRefWrapper(self.__channel,method,actor.url))
        for method in actor.tell_ref:
            setattr(self, method, TellRefWrapper(self.__channel,method,actor.url))

        for method in actor.tell:
            setattr(self, method, TellWrapper(self.__channel,method,actor.url))
        for method in actor.ask:
            setattr(self, method, AskWrapper(self.__channel,method,actor.url))

    def __repr__(self):
        return 'Proxy(actor=%s, tell=%s ref=%s, ask=%s ref=%s)' % (self.actor, self.actor.tell,
                                        self.actor.tell_ref,self.actor.ask, self.actor.ask_ref)




class Future(object):
    '''
    Future manages the remote method invocations that returns a result.
    Mostly for ask requests.
    '''
    def __init__(self,actor_channel,method,params,actor_url):
        self.__channel = Channel()
        self.__method = method
        self.__params = params
        self.__actor_channel = actor_channel
        self.__target = actor_url

    def __getattr__(self, name):
        raise Exception("'Future' object has no attribute %r. Remember to call get() after an ask query." % name)

    def get(self,timeout=1):
        '''
        Invokes the method sending a query through the channel and obtains the
        result of this method.

        It is necessary to invoke this method with a synchronous query in order
        to get the result. As in :ref:`sample2`::

            e1.say_something().get()

        Unless you use this method, you will get the future itself, which means
        the method has not been invoked yet, like in :ref:`sample3`::

            future = self.echo.say_something()

        In this case, you could set a callback with :meth:`add_callback`, so the
        result will be sent to the method you specify.

        :param int timeout: timeout to wait for the result. If not specified,
            it's set to 1 sec.
        :returns: the result of the invoked method. Could be any type.
        :raises: :class:`Timeout`, or an error receiving from the channel.
        '''
        ##  SENDING MESSAGE ASK
        msg = AskRequest(ASK,self.__method,self.__params,self.__channel,self.__target)
        self.__actor_channel.send(msg)
        try:
            response = self.__channel.receive(timeout)
            result = response.result
            if isinstance(result, Exception):
                raise result
            else:
                return result
        except AlreadyExists, ae:
            raise ae
        except Empty,e:
            raise Timeout()

    def add_callback(self,callback):
        '''
        Sets a callback on the Future. This will generate a new
        :class:`~.FutureRequest` sent to the actor that will invoke
        the callback function with the result by parameter.

        In :ref:`sample3` you can see how to use it::

            future = self.echo.say_something()
            future.add_callback('pong')

        pong is a method of the same class that receives the result of the query
        in parameter *msg*::

            def pong(self,msg):
                print 'callback',msg

        :param str. callback: name of the function where to send the response.
        '''
        from_actor = get_current()
        ##  SENDING MESSAGE FUTURE
        #msg = (_from, self.target, FUTURE, self.method,self.params,callback,actors[_from].channel)
        msg = FutureRequest(FUTURE,self.__method,self.__params,callback,
                                from_actor.channel,self.__target,from_actor.url)
        self.__actor_channel.send(msg)

class FutureRef(Future):
    def get(self,timeout=1):
        result = super(FutureRef,self).get(timeout)
        return get_host()._loads(result)

class TellWrapper(object):
    '''
    Wrapper for Tell type queries to the proxy. Creates the request and sends it
    through the channel.

    :param Channel channel: communication way for the query.
    :param str. method: name of the method this query is gonna invoke.
    :param str. actor_url: URL address where the actor is set.
    '''
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

class AskWrapper(object):
    '''
    Wrapper for Ask type queries to the proxy. Creates a :class:`Future` to
    manage the result reply.

    :param Channel channel: communication way for the query.
    :param str. method: name of the method this query is gonna invoke.
    :param str. actor_url: URL address where the actor is set.
    '''
    def __init__(self, channel, method,actor_url):
        self._channel = channel
        self._method = method
        self.target = actor_url

    def __call__(self, *args, **kwargs):
        return Future(self._channel,self._method,args, self.target)

class AskRefWrapper(AskWrapper):
    def __call__(self, *args, **kwargs):
        new_args = get_host()._dumps(list(args))
        return FutureRef(self._channel,self._method,new_args, self.target)

class TellRefWrapper(TellWrapper):
    def __call__(self, *args, **kwargs):
        new_args = get_host()._dumps(list(args))
        result = super(TellRefWrapper,self).__call__(*new_args, **kwargs)
