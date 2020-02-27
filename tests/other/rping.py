"""
PING-PONG test. Messages per second. REMOTE PING
@author: Daniel Barcelona Pons
"""

from time import time

from pyactor.context import set_context, create_host, sleep, shutdown

N = 100
working = True


class Message(object):
    pass


class StartMessage(Message):
    pass


class PingMessage(Message):
    pass


class SendPongMessage(Message):
    pass


class SendPingMessage(Message):
    pass


class StopMessage(Message):
    pass


class PingActor(object):
    _tell = {'send'}

    def __init__(self, count, pong):
        self.pingsLeft = count
        self.pong = pong

    def send(self, msg):
        if isinstance(msg, StartMessage):
            ping = SendPingMessage()
            # print 'ping'
            self.pong.send(ping)
            self.pingsLeft = self.pingsLeft - 1
        elif isinstance(msg, PingMessage):
            ping = SendPingMessage()
            # print 'ping'
            # print self.pingsLeft
            self.pong.send(ping)
            self.pingsLeft = self.pingsLeft - 1
        elif isinstance(msg, SendPongMessage):
            if self.pingsLeft > 0:
                msg = PingMessage()
                self.send(msg)
            else:
                msg = StopMessage()
                self.pong.send(msg)
        elif isinstance(msg, StopMessage):
            global working
            working = False
            self.proxy.stop()
        else:
            raise Exception("Unsupported message: " + msg.__class__.__name__)


if __name__ == '__main__':
    set_context()
    host = create_host("amqp://127.0.0.1:9111/")

    pong = host.lookup_url("amqp://127.0.0.1:9000/pong", 'PongActor', 'rpong')
    ping = host.spawn('ping', PingActor, N, pong)

    pong.set_ping(ping)
    init = time()

    msg = StartMessage()
    ping.send(msg)

    while working:
        sleep(1)

    end = time()

    print(end - init, "s")

    shutdown()
