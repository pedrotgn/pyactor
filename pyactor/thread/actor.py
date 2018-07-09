from copy import copy
from threading import Thread

from .channel import Channel
from .future import FutureManager
from ..util import ASK, TELL, FUTURE, TYPE, ASK_RESPONSE, FUTURE_RESPONSE
from ..util import METHOD, PARAMS, RESULT, CHANNEL, RPC_ID
from ..util import ref_l, ref_d


class ActorRef(object):
    """
    ActorRef contains the main components of an actor. These are the
    URL where it is located, the communication :class:`~.Channel` and
    the class of the actor as also the synchronous and asynchronous
    methods the class implements. When no channel is specified a new
    one will be created which is also the default procedure.

    .. note:: This is a superclass of :py:class:`Actor` and has no
        direct functionality.

    """

    def __init__(self, url, klass, channel=None):
        self.url = url
        self.tell = []
        self.ask = []
        self.klass = klass
        if channel:
            self.channel = channel
        else:
            self.channel = Channel()
        if hasattr(klass, '_tell') and klass._tell:
            self.tell = copy(klass._tell)
        if hasattr(klass, '_ask') and klass._ask:
            self.ask = copy(klass._ask)

        if hasattr(klass, '_ref'):
            self.receive = ref_l(self, self.receive)
            self.send_response = ref_d(self, self.send_response)

            self.tell_ref = list(set(self.tell) & set(klass._ref))
            self.ask_ref = list(set(self.ask) & set(klass._ref))
            for method in self.ask_ref:
                self.ask.remove(method)
            for method in self.tell_ref:
                self.tell.remove(method)
        else:
            self.ask_ref = []
            self.tell_ref = []

        self.tell.append('stop')

    def receive(self, msg):
        raise NotImplementedError()

    def send_response(self, result, msg):
        raise NotImplementedError()

    @property
    def _ref(self):
        return list(set(self.tell_ref) | set(self.ask_ref))

    def __str__(self):
        return f'Actor {self.url} ({self.klass.__name__})'

    def __repr__(self):
        return f'Actor(url={self.url}, class={self.klass})'


class Actor(ActorRef):
    """
    Actor is the instance of an object to which is possible to access
    and invoke its methods remotely. Main element of the model. The
    host is the one to create them (spawning -> see :meth:`~.spawn`).

    :param str. url: URL where the actor is running.
    :param class klass: class type for the actor.
    :param klass obj: instance of the *klass* class to attach to the
        actor.
    """

    def __init__(self, url, klass, obj):
        super(Actor, self).__init__(url, klass)
        self._obj = obj
        self.id = obj.id
        self.running = True
        self.future_manager = FutureManager()

    def __process_queue(self):
        while self.running:
            message = self.channel.receive()
            self.receive(message)

    def is_alive(self):
        """
        :return: (*bool.*) identifies the current state of the actor.
            **True** if it is running.
        """
        return self.running

    def receive(self, msg):
        """
        The message received from the queue specify a method of the
        class the actor represents. This invokes it. If the
        communication is an ASK, sends the result back
        to the channel included in the message as an
        ASK_RESPONSE.

        If it is a FUTURE, generates a FUTURE_RESPONSE
        to send the result to the manager.

        :param msg: The message is a dictionary using the constants
            defined in util.py (:mod:`pyactor.util`).
        """
        if msg[TYPE] == TELL and msg[METHOD] == 'stop':
            self.running = False
            self.future_manager.stop()
        else:
            try:
                invoke = getattr(self._obj, msg[METHOD])
                params = msg[PARAMS]
                result = invoke(*params[0], **params[1])
            except Exception as e:
                if msg[TYPE] == TELL:
                    print(e)
                    return
                result = e
            self.send_response(result, msg)

    def send_response(self, result, msg):
        if msg[TYPE] == ASK:
            response = {TYPE: ASK_RESPONSE, RESULT: result,
                        RPC_ID: msg[RPC_ID] if RPC_ID in msg.keys() else None}
            # AskResponse(result)
            msg[CHANNEL].send(response)
        elif msg[TYPE] == FUTURE:
            response = {TYPE: FUTURE_RESPONSE, RPC_ID: msg[RPC_ID],
                        RESULT: result}
            msg[CHANNEL].send(response)

    def run(self):
        """
        Creates the actor thread which will process the channel queue
        while the actor :meth:`is_alive`, making it able to receive
        queries.
        """
        self.thread = Thread(target=self.__process_queue)
        self.thread.start()
