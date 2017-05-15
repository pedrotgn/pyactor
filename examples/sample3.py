'''
Callback sample.
'''
from pyactor.context import set_context, create_host, sleep, shutdown


class Echo(object):
    _tell = ['echo', 'bye']
    _ask = ['say_something']

    def echo(self, msg):
        print msg

    def bye(self):
        print 'bye'

    def say_something(self):
        sleep(1)
        return 'something'


class Bot(object):
    _tell = ['set_echo', 'ping', 'pong']
    _ask = []
    _ref = ['set_echo']

    def set_echo(self, echo):
        self.echo = echo

    def ping(self):
        future = self.echo.say_something(future=True)
        future.add_callback('pong')
        future.add_callback('pong')
        print 'pinging..'

    def pong(self, future):
        msg = future.result()
        print 'callback', msg


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    bot = h.spawn('bot', Bot)
    bot.set_echo(e1)
    bot.ping()

    sleep(2)
    shutdown()
