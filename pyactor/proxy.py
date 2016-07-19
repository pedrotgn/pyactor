from Queue import Empty

from util import ASK, FUTURE, TELL
from util import AskRequest, FutureRequest, TellRequest
from util import AlreadyExistsError, TimeoutError, NotFoundError
from util import get_current, get_host, get_lock


def set_actor(module_name):
    global actorm
    actorm = __import__(module_name + '.actor', globals(), locals(),
                        ['Channel'], -1)
    global future
    future = __import__(module_name + '.future', globals(), locals(),
                        ['Future'], -1)


class Proxy(object):
    '''
    Proxy is the class that supports to create a remote reference to an
    actor and invoke its methods.

    :param Actor actor: the actor the proxy will manage.
    '''
    def __init__(self, actor):
        self.__channel = actor.channel
        self.actor = actor
        self.__lock = get_lock()
        # print "At proxy",self.__lock#, self.actor
        for method in actor.ask_ref:
            setattr(self, method, AskRefWrapper(self.__channel, method,
                                                actor.url))
        for method in actor.tell_ref:
            setattr(self, method, TellRefWrapper(self.__channel, method,
                                                 actor.url))

        for method in actor.tell:
            setattr(self, method, TellWrapper(self.__channel, method,
                                              actor.url))
        for method in actor.ask:
            setattr(self, method, AskWrapper(self.__channel, method,
                                             actor.url))

    def __repr__(self):
        return 'Proxy(actor=%s, tell=%s ref=%s, ask=%s ref=%s)' % \
               (self.actor, self.actor.tell, self.actor.tell_ref,
                self.actor.ask, self.actor.ask_ref)


class TellWrapper(object):
    '''
    Wrapper for Tell type queries to the proxy. Creates the request and
    sends it through the channel.

    :param Channel channel: communication way for the query.
    :param str. method: name of the method this query is gonna invoke.
    :param str. actor_url: URL address where the actor is set.
    '''
    def __init__(self, channel, method, actor_url):
        self.__channel = channel
        self.__method = method
        self.__target = actor_url

    def __call__(self, *args, **kwargs):
        # _from = get_current()
        #  SENDING MESSAGE TELL
        # msg = (_from, self.__target, TELL, self.__method,args)
        msg = TellRequest(TELL, self.__method, args, self.__target)
        self.__channel.send(msg)


class AskWrapper(object):
    '''
    Wrapper for Ask type queries to the proxy. Creates a :class:`Future`
    to manage the result reply.

    :param Channel channel: communication way for the query.
    :param str. method: name of the method this query is gonna invoke.
    :param str. actor_url: URL address where the actor is set.
    '''
    def __init__(self, channel, method, actor_url):
        self.__actor_channel = channel
        self.__method = method
        self.target = actor_url

    def __call__(self, *args, **kwargs):
        future = kwargs['future'] if 'future' in kwargs.keys() else False

        if not future:
            self.__channel = actorm.Channel()
            self.__lock = get_lock()
            timeout = kwargs['timeout'] if 'timeout' in kwargs.keys() else 1
            #  SENDING MESSAGE ASK
            msg = AskRequest(ASK, self.__method, args, self.__channel,
                             self.target)
            self.__actor_channel.send(msg)
            if self.__lock:
                self.__lock.release()
            try:
                response = self.__channel.receive(timeout)
                result = response.result
                if self.__lock:
                    self.__lock.acquire()
                if isinstance(result, Exception):
                    raise result
                else:
                    return result
            except AlreadyExistsError, ae:
                raise ae
            except NotFoundError, nf:
                raise nf
            except Empty:
                if self.__lock:
                    self.__lock.acquire()
                raise TimeoutError(self.__method)
        else:
            return get_host().future_manager.new_future(self.__method, args,
                                                        self.__actor_channel,
                                                        self.target)


class AskRefWrapper(AskWrapper):
    '''
    Wrapper for Ask queries that have a proxy in parameters or returns.
    '''
    def __call__(self, *args, **kwargs):
        future = kwargs['future'] if 'future' in kwargs.keys() else False
        new_args = get_host().dumps(list(args))
        if future:
            return get_host().future_manager.new_future(self.__method, args,
                                                        self.__actor_channel,
                                                        self.target, ref=True)
        else:
            result = super(AskRefWrapper, self).__call__(*new_args, **kwargs)
            return get_host().loads(result)


class TellRefWrapper(TellWrapper):
    '''Wrapper for Tell queries that have a proxy in parameters.'''
    def __call__(self, *args, **kwargs):
        new_args = get_host().dumps(list(args))
        return super(TellRefWrapper, self).__call__(*new_args, **kwargs)
