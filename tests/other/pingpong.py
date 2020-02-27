"""
PING-PONG test. Messages per second.
@author: Daniel Barcelona Pons
"""

from time import time

from pyactor.context import set_context, create_host, sleep, shutdown

N = 1000000


class Message(object):
    pass


class StartMessage(Message):
    pass


class PingMessage(Message):
    pass


class SendPongMessage(Message):
    def __init__(self, sender):
        self.sender = sender


class SendPingMessage(Message):
    def __init__(self, sender):
        self.sender = sender


class StopMessage(Message):
    pass


class PingActor(object):
    _tell = ['send']

    def __init__(self, count, pong):
        self.pingsLeft = count
        self.pong = pong

    def send(self, msg):
        if isinstance(msg, StartMessage):
            ping = SendPingMessage(self.proxy)
            # print 'ping'
            self.pong.send(ping)
            self.pingsLeft = self.pingsLeft - 1
        elif isinstance(msg, PingMessage):
            ping = SendPingMessage(self.proxy)
            # print 'ping'
            self.pong.send(ping)
            self.pingsLeft = self.pingsLeft - 1
        elif isinstance(msg, SendPongMessage):
            if self.pingsLeft > 0:
                msg = PingMessage()
                self.send(msg)
            else:
                msg = StopMessage()
                self.pong.send(msg)
                self.proxy.stop()
        else:
            raise Exception("Unsupported message: " + msg.__class__.__name__)


class PongActor(object):
    _tell = ['send']

    pongCount = 0

    def send(self, msg):
        if isinstance(msg, SendPingMessage):
            sender = msg.sender
            # print 'pong'
            pong = SendPongMessage(self.proxy)
            sender.send(pong)
            self.pongCount = self.pongCount + 1
        elif isinstance(msg, StopMessage):
            self.proxy.stop()

        else:
            raise Exception("Unsupported message: " + msg)


if __name__ == '__main__':
    set_context('green_thread')
    host = create_host()

    pong = host.spawn('pong', PongActor)
    ping = host.spawn('ping', PingActor, N, pong)

    init = time()

    msg = StartMessage()
    ping.send(msg)

    while pong.actor.is_alive():
        sleep(0.1)

    end = time()

    print((end - init), ' s.')

    shutdown()
