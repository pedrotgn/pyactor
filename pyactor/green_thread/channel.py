from gevent.queue import Queue


class Channel(Queue):
    """
    Channel is the main communication mechanism between actors. It is
    actually a simple facade to the gevent.Queue class.
    """

    def __init__(self):
        Queue.__init__(self)

    def send(self, msg):
        """
        It sends a message to the current channel.

        :param msg: The message sent to an actor. It is a dictionary
            using the constants in util.py (:mod:`pyactor.util`).
        """
        self.put(msg)

    def receive(self, timeout=None):
        """
        It receives a message from the channel, blocking the calling
        thread until the response is received, or the timeout is
        triggered.

        :param int timeout: timeout to wait for messages. If none
            provided it will block until a message arrives.
        :return: returns a message sent to the channel. It is a
            dictionary the constants in util.py (:mod:`pyactor.util`).
        """
        return self.get(timeout=timeout)
