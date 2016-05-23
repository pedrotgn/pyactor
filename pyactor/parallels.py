from pyactor.actor import *
import uuid
from threading import Lock


class ActorParallel(Actor):
    '''
    Actor with parallel methods.
    '''
    def __init__(self, url, klass, obj):
        super(ActorParallel,self).__init__(url,klass,obj)
        self.pthreads = []
        self.pending = {}
        self.sync_parallel = set(klass._ask)&set(klass._parallel)
        self.async_parallel = set(klass._tell)&set(klass._parallel)

        self.__lock = Lock()
        for method in self.sync_parallel:
            setattr(self._obj, method, ParallelSyncWraper(getattr(self._obj, method), self, self.__lock))
        for method in self.async_parallel:
            setattr(self._obj, method, ParallelAsyncWraper(getattr(self._obj, method), self, self.__lock))

    def receive(self,msg):
        '''
        The message received from the queue specify a method of the class the
        actor represents. This invokes it. If the communication is an
        :class:`~.AskRequest`, sends the result back to the channel included in
        the message as an :class:`~.AskResponse`.
        If it is a :class:`~.Future`, generates a :class:`~.TellRequest` to send
        the result to the sender's method specified in the callback field of the
        tuple.

        :param msg: The message is a namedtuple of the defined in util.py
            (:class:`~.AskRequest`, :class:`~.TellRequest`, :class:`~.FutureRequest`).
        '''
        if msg.method=='stop':
            for t in self.pthreads:
                t.join()
            self.running = False

        else:
            result = None
            try:
                invoke = getattr(self._obj, msg.method)
                params = msg.params

                if msg.method in self.sync_parallel:
                    rpc_id = str(uuid.uuid4())
                    # add rpc message to pendent AskResponse s
                    self.pending[rpc_id] = msg
                    # insert an rpc id to args
                    params = list(params)
                    params.insert(0, rpc_id)
                    invoke(*params)
                    return

                else:
                    #self.__lock.acquire()
                    result = invoke(*params)
                    #self.__lock.release()
            except Exception, e:
                result = e
                print result

        if msg.type == ASK:
            response = AskResponse(result)
            msg.channel.send(response)
        if msg.type == FUTURE:
            response = TellRequest(TELL,msg.callback,[result],msg.from_url)
            msg.channel.send(response)

    def receive_sync(self, result, rpc_id):
        msg = self.pending[rpc_id]
        del self.pending[rpc_id]
        response = AskResponse(result)
        msg.channel.send(response)

    def get_lock(self):
        return self.__lock


class ParallelSyncWraper():
    def __init__(self, method, actor, lock):
        self.__method = method
        self.__actor = actor
        self.__lock = lock
    def __call__(self, *args, **kwargs):
        try:
            args = list(args)
            rpc_id = args[0]
            del args[0]
            args = tuple(args)
        except:
            rpc_id = None
        finally:
            if not rpc_id:
                result = self.__method(*args)
                return result
            else:
                t1 = Thread(target=self.invoke, args=(self.__method,rpc_id, args,kwargs))
                t1.start()
                self.__actor.pthreads.append(t1)

    def invoke(self, func, rpc_id, args=[], kwargs=[]):
        #self.__lock.acquire()
        try:
            result = func(*args)
        except Exception,e:
            result= e
        #self.__lock.release()
        self.__actor.receive_sync(result, rpc_id)


class ParallelAsyncWraper():
    def __init__(self, method, actor, lock):
        self.__method = method
        self.__actor = actor
        self.__lock = lock
    def __call__(self, *args, **kwargs):
        t1 = Thread(target=self.invoke, args=(self.__method, args, kwargs))
        t1.start()
        self.__actor.pthreads.append(t1)

    def invoke(self, func, args=[], kwargs=[]):
        #self.__lock.acquire()
        func(*args, **kwargs)
        #self.__lock.release()
