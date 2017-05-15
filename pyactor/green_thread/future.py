import uuid
from gevent import spawn
from gevent.event import Event

from pyactor.util import get_current, get_host, RPC_ID, RESULT
from pyactor.util import TELL, FUTURE, TYPE, METHOD, PARAMS, CHANNEL, TO
from pyactor.exceptions import TimeoutError, FutureError
from pyactor.green_thread import Channel


PENDING = 'PENDING'
RUNNING = 'RUNNING'
FINISHED = 'FINISHED'


class Future(object):
    """
    Container for the result of an ask query sent asynchronously which
    could not be resolved yet.
    """
    def __init__(self, fid, future_ref, manager_channel):
        self.__condition = Event()
        self.__state = PENDING
        self.__result = None
        self.__exception = None
        self.__callbacks = []

        self.__method = future_ref[METHOD]
        self.__params = future_ref[PARAMS]
        self.__actor_channel = future_ref[CHANNEL]
        self.__target = future_ref[TO]
        self.__channel = manager_channel
        self.__id = fid

    def _invoke_callbacks(self):
        for callback in self.__callbacks:
            try:
                # msg = TellRequest(TELL, callback[0], [self], callback[2])
                msg = {TYPE: TELL, METHOD: callback[0], PARAMS: [self],
                       TO: callback[2]}
                callback[1].send(msg)
            except Exception, e:
                raise FutureError('Exception calling callback for %r: %r'
                                  % (self, e))

    def running(self):
        """Return True if the future is currently executing."""
        # with self.__condition:
        return self.__state == RUNNING

    def done(self):
        """Return True if the future finished executing."""
        # with self.__condition:
        return self.__state == FINISHED

    def __get__result(self):
        if self.__exception is not None:
            raise self.__exception
        else:
            return self.__result

    def add_callback(self, method):
        """
        Attaches a mehtod that will be called when the future finishes.

        :param method: A callable from an actor that will be called
            when the future completes. The only argument for that
            method must be the future itself from wich you can get the
            result though `future.:meth:`result()``. If the future has
            already completed, then the callable will be called
            immediately.

        .. note:: This functionallity only works when called from an actor,
            specifying a method from the same actor.
        """
        from_actor = get_current()
        if from_actor is not None:
            callback = (method, from_actor.channel, from_actor.url)
            # with self.__condition:
            if self.__state is not FINISHED:
                self.__callbacks.append(callback)
                return
            # Invoke the callback directly
            # msg = TellRequest(TELL, method, [self], from_actor.url)
            msg = {TYPE: TELL, METHOD: method, PARAMS: [self],
                   TO: from_actor.url}
            from_actor.channel.send(msg)
        else:
            raise FutureError("add_callback only works when called " +
                              "from inside an actor")

    def result(self, timeout=None):
        """Returns the result of the call that the future represents.

        :param timeout: The number of seconds to wait for the result
            if the future has not been completed. None, the default,
            sets no limit.
        :returns: The result of the call that the future represents.
        :raises: TimeoutError: If the timeout is reached before the
            future ends execution.
        :raises: Exception: If the call raises the Exception.
        """
        # with self.__condition:
        if self.__state == FINISHED:
            return self.__get__result()

        self.__condition.wait(timeout)

        if self.__state == FINISHED:
            return self.__get__result()
        else:
            raise TimeoutError('Future: %r' % self.__method)

    def exception(self, timeout=None):
        """Return a exception raised by the call that the future
        represents.
        :param timeout: The number of seconds to wait for the exception
            if the future has not been completed. None, the default,
            sets no limit.
        :returns: The exception raised by the call that the future
            represents or None if the call completed without raising.
        :raises: TimeoutError: If the timeout is reached before the
            future ends execution.
        """
        # with self.__condition:
        if self.__state == FINISHED:
            return self.__exception

        self.__condition.wait(timeout)

        if self.__state == FINISHED:
            return self.__exception
        else:
            raise TimeoutError('Future: %r' % self.__method)

    def send_work(self):
        '''Sends the query to the actor for it to start executing the
        work.

        It is possible to execute once again a future that has finished
        if necessary (overwriting the results), but only one execution
        at a time.
        '''
        if self.__set_running():
            # msg = FutureRequest(FUTURE, self.__method, self.__params,
            #                     self.__channel, self.__target, self.__id)
            msg = {TYPE: FUTURE, METHOD: self.__method, PARAMS: self.__params,
                   CHANNEL: self.__channel, TO: self.__target,
                   RPC_ID: self.__id}
            self.__actor_channel.send(msg)
        else:
            raise FutureError("Future already running.")

    def __set_running(self):
        # """This is only called internally from send_work().
        # It marks the future as running or returns false if it
        # already was running."""
        # with self.__condition:
        if self.__state in [PENDING, FINISHED]:
            self.__condition.clear()
            self.__state = RUNNING
            return True
        elif self.__state == RUNNING:
            return False

    def set_result(self, result):
        """Sets the return value of work associated with the future.
        Only called internally.
        """
        # with self.__condition:
        self.__result = result
        self.__state = FINISHED
        self.__condition.set()
        self._invoke_callbacks()

    def set_exception(self, exception):
        """Sets the result of the future as being the given exception.
        Only called internally.
        """
        # with self.__condition:
        self.__exception = exception
        self.__state = FINISHED
        self.__condition.set()
        self._invoke_callbacks()


class FutureRef(Future):
    def result(self, timeout=None):
        """Returns the result of the call that the future represents.

        :param timeout: The number of seconds to wait for the result
            if the future has not been completed. None, the default,
            sets no limit.
        :returns: The result of the call that the future represents.
        :raises: TimeoutError: If the timeout is reached before the
            future ends execution.
        :raises: Exception: If the call raises the Exception.
        """
        result = super(FutureRef, self).result(timeout)
        return get_host().loads(result)


class FutureManager(object):
    '''
    A manager that controls the creation and execution of the futures.
    '''
    def __init__(self):
        self.running = False
        self.channel = Channel()
        self.futures = {}
        self.t = None

    def __queue_management(self):
        self.running = True
        while self.running:
            response = self.channel.receive()
            if response == 'stop':
                self.running = False
            else:
                result = response[RESULT]
                future = self.futures[response[RPC_ID]]
                if isinstance(result, Exception):
                    future.set_exception(result)
                else:
                    future.set_result(result)

    def new_future(self, future_ref, ref=False):
        future_id = str(uuid.uuid4())
        if not ref:
            future = Future(future_id, future_ref, self.channel)
        else:
            future = FutureRef(future_id, future_ref, self.channel)
        future.send_work()
        self.futures[future_id] = future

        if not self.running:
            self.t = spawn(self.__queue_management)
        return future

    def stop(self):
        self.channel.send('stop')
        if self.t is not None:
            self.t.join()
            self.t = None
        self.futures = {}
