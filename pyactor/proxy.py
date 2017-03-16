from Queue import Empty

from util import ASK, TELL, TYPE, METHOD, PARAMS, CHANNEL, TO, RESULT
from exceptions import TimeoutError, NotFoundError, HostError
from util import get_host, get_lock


def set_actor(module_name):
    global actorm
    actorm = __import__(module_name + '.actor', globals(), locals(),
                        ['Channel'], -1)
    global future
    future = __import__(module_name + '.future', globals(), locals(),
                        ['Future'], -1)


class ProxyRef(object):
    def __init__(self, actor, kclass, modul):
        self.url = actor
        self.klass = kclass
        self.module = modul

    def __repr__(self):
        return 'ProxyRef(actor=%s, class=%s mod=%s)' % \
               (self.url, self.klass, self.module)


class Proxy(object):
    '''
    Proxy is the class that supports to create a remote reference to an
    actor and invoke its methods. All the references to actors will be
    proxies, even the host.
    To get aproxy to an Actor, you should use one of the host functions
    that provide one, like :meth:`~.spawn` or :meth:`~.lookup_url`.

    :param Actor actor: the actor the proxy will manage.
    '''
    def __init__(self, actor):
        self.__channel = actor.channel
        self.actor = actor
        self.__lock = get_lock()
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

    def __str__(self):
        return '%s\'s proxy' % (self.actor,)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.actor.url == other.actor.url
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self == other
        return NotImplemented

    def __hash__(self):
        return hash(self.actor)

    def get_id(self):
        return self.actor.id

    def get_url(self):
        return self.actor.url


class TellWrapper(object):
    '''
    Wrapper for Tell type queries to the proxy. Creates the request and
    sends it through the channel.

    :param Channel channel: communication way for the query.
    :param str. method: name of the method this query is going to invoke.
    :param str. actor_url: URL address where the actor is set.
    '''
    def __init__(self, channel, method, actor_url):
        self.__channel = channel
        self.__method = method
        self.__target = actor_url

    def __call__(self, *args, **kwargs):
        #  SENDING MESSAGE TELL
        # msg = TellRequest(TELL, self.__method, args, self.__target)
        msg = {TYPE: TELL, METHOD: self.__method, PARAMS: args,
               TO: self.__target}
        self.__channel.send(msg)


class AskWrapper(object):
    '''
    Wrapper for Ask type queries to the proxy. Calling it blocks the
    execution until the result is returned or timeout is reached. You
    can add the tagged parameter "timeout" to change the time limit to
    wait. It is also possible to specify "future=True" to get an instant
    response with a :class:`Future` object with which one you can
    manage the result reply.

    :param Channel channel: communication way for the query.
    :param str. method: name of the method this query is gonna invoke.
    :param str. actor_url: URL address where the actor is set.
    '''
    def __init__(self, channel, method, actor_url):
        self._actor_channel = channel
        self._method = method
        self.target = actor_url

    def __call__(self, *args, **kwargs):
        future = kwargs['future'] if 'future' in kwargs.keys() else False

        self.__lock = get_lock()
        if not future:
            self.__channel = actorm.Channel()
            timeout = kwargs['timeout'] if 'timeout' in kwargs.keys() else 1
            #  SENDING MESSAGE ASK
            # msg = AskRequest(ASK, self._method, args, self.__channel,
            #                  self.target)
            msg = {TYPE: ASK, METHOD: self._method, PARAMS: args,
                   CHANNEL: self.__channel, TO: self.target}
            self._actor_channel.send(msg)
            if self.__lock is not None:
                self.__lock.release()
            try:
                response = self.__channel.receive(timeout)
                result = response[RESULT]
            except Empty:
                if self.__lock is not None:
                    self.__lock.acquire()
                raise TimeoutError(self._method)
            if self.__lock is not None:
                self.__lock.acquire()
            if isinstance(result, Exception):
                raise result
            else:
                return result
        else:
            future_ref = {METHOD: self._method, PARAMS: args,
                          CHANNEL: self._actor_channel, TO: self.target,
                          'LOCK': self.__lock}
            return get_host().future_manager.new_future(future_ref)


class AskRefWrapper(AskWrapper):
    '''
    Wrapper for Ask queries that have a proxy in parameters or returns.
    '''
    def __call__(self, *args, **kwargs):
        future = kwargs['future'] if 'future' in kwargs.keys() else False
        host = get_host()
        if host is not None:
            new_args = host.dumps(list(args))
        else:
            raise HostError('No such Host on the context of the call.')

        if future:
            self.__lock = get_lock()
            future_ref = {METHOD: self._method, PARAMS: args,
                          CHANNEL: self._actor_channel, TO: self.target,
                          'LOCK': self.__lock}
            return get_host().future_manager.new_future(future_ref, ref=True)
        else:
            result = super(AskRefWrapper, self).__call__(*new_args, **kwargs)
            return get_host().loads(result)


class TellRefWrapper(TellWrapper):
    '''Wrapper for Tell queries that have a proxy in parameters.'''
    def __call__(self, *args, **kwargs):
        host = get_host()
        if host is not None:
            new_args = host.dumps(list(args))
        else:
            raise HostError('No such Host on the context of the call.')
        return super(TellRefWrapper, self).__call__(*new_args, **kwargs)
