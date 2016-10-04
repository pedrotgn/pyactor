import uuid

from gevent import spawn
from pyactor.util import get_host, METHOD, PARAMS
from actor import Actor


class ActorParallel(Actor):
    '''
    Actor with parallel methods. Parallel methods are invoked in new
    threads, so their invocation do not block the actor allowing it to
    process many queries at a time.
    Green threads do not have concurrernce problems so no need to use
    Locks in this implementation.
    '''
    def __init__(self, url, klass, obj):
        super(ActorParallel, self).__init__(url, klass, obj)
        self.pending = {}
        self.ask_parallel = list((set(self.ask) | set(self.ask_ref)) &
                                 set(klass._parallel))
        self.tell_parallel = list((set(self.tell) | set(self.tell_ref)) &
                                  set(klass._parallel))

        for method in self.ask_parallel:
            setattr(self._obj, method,
                    ParallelAskWraper(getattr(self._obj, method), self))
        for method in self.tell_parallel:
            setattr(self._obj, method,
                    ParallelTellWraper(getattr(self._obj, method), self))

    def receive(self, msg):
        '''
        Overwriting :meth:`Actor.receive`, adds the checks and
        functionalities requiered by parallel methods.

        :param msg: The message is a dictionary using the constants
            defined in util.py (:mod:`pyactor.util`).
        '''
        if msg[METHOD] == 'stop':
            self.running = False
        else:
            result = None
            try:
                invoke = getattr(self._obj, msg[METHOD])
                params = msg[PARAMS]

                if msg[METHOD] in self.ask_parallel:
                    rpc_id = str(uuid.uuid4())
                    # add rpc message to pendent AskResponse s
                    self.pending[rpc_id] = msg
                    # insert an rpc id to args
                    params = list(params)
                    params.insert(0, rpc_id)
                    invoke(*params)
                    return
                else:
                    result = invoke(*params)
            except Exception, e:
                result = e
                print result
            self.send_response(result, msg)

    def receive_from_ask(self, result, rpc_id):
        msg = self.pending[rpc_id]
        del self.pending[rpc_id]
        self.send_response(result, msg)

# For compatibility. Green threads do no use Locks.
    def get_lock(self):
        return None


class ParallelAskWraper(object):
    '''Wrapper for ask methods that have to be called in a parallel form.'''
    def __init__(self, method, actor):
        self.__method = method
        self.__actor = actor

    def __call__(self, *args, **kwargs):
        args = list(args)
        rpc_id = args[0]
        del args[0]
        args = tuple(args)

        param = (self.__method, rpc_id, args, kwargs)
        t = spawn(self.invoke, *param)  # New thread
        get_host().new_parallel(self.__actor.url, t)

    def invoke(self, func, rpc_id, args, kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception, e:
            result = e
        self.__actor.receive_from_ask(result, rpc_id)


class ParallelTellWraper(object):
    '''
    Wrapper for tell methods that have to be called in a parallel form.
    '''
    def __init__(self, method, actor):
        self.__method = method
        self.__actor = actor

    def __call__(self, *args, **kwargs):
        param = (self.__method, args, kwargs)
        t = spawn(self.invoke, *param)
        get_host().new_parallel(self.__actor.url, t)

    def invoke(self, func, args, kwargs):
        func(*args, **kwargs)
