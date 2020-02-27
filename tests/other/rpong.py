"""
PING-PONG test. Messages per second. REMOTE PONG
@author: Daniel Barcelona Pons
"""

from pyactor.context import set_context, create_host, serve_forever


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


class PongActor(object):
    _tell = {'send', 'set_ping'}
    _ref = {'set_ping'}

    pongCount = 0

    def set_ping(self, ping):
        self.ping = ping

    def send(self, msg):
        if isinstance(msg, SendPingMessage):
            # print 'pong'
            pong = SendPongMessage()
            self.ping.send(pong)
            self.pongCount = self.pongCount + 1
        elif isinstance(msg, StopMessage):
            self.ping.send(msg)
            self.proxy.stop()

        else:
            raise Exception("Unsupported message: " + msg)


if __name__ == '__main__':
    set_context()
    host = create_host("amqp://127.0.0.1:9000/")

    pong = host.spawn('pong', PongActor)

    serve_forever()
