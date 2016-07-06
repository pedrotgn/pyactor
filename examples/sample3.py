'''
Callback sample.
'''
from pyactor.context import set_context, create_host, sleep


class Echo(object):
    _tell = ['echo', 'bye']
    _ask = ['say_something']

    def echo(self, msg):
        print msg

    def bye(self):
        print 'bye'

    def say_something(self):
        return 'something'


class Bot(object):
    _tell = ['set_echo', 'ping', 'pong']
    _ask = []

    def set_echo(self, echo):
        self.echo = echo

    def ping(self):
        future = self.echo.say_something()
        future.add_callback('pong')
        print 'pinging..'

    def pong(self, msg):
        print 'callback', msg

set_context()
h = create_host()
e1 = h.spawn('echo1', Echo)
bot = h.spawn('bot', Bot)
bot.set_echo(e1)
bot.ping()

sleep(1)
h.shutdown()
