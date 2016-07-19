'''
Futures Sample.
'''
from pyactor.context import set_context, create_host, sleep


class Echo(object):
    _tell = ['echo', 'bye']
    _ask = ['say_something', 'raise_something']

    def echo(self, msg):
        print msg

    def say_something(self):
        return 'something'

    def raise_something(self):
        raise Exception('raising something')


class Bot(object):
    _tell = ['set_echo', 'ping', 'pong']
    _ask = []

    def set_echo(self):
        self.echo = self.host.lookup('echo1')

    def ping(self, bot=None):
        future = self.echo.say_something(future=True)
        print 'pinging..'
        if bot is not None:
            future.add_callback('pong', bot)
            future.add_callback('pong', bot)
        future.add_callback('pong')
        sleep(1)
        print 'late callback:'
        future.add_callback('pong')

    def pong(self, future):
        msg = future.result()
        print self.id, ': callback', msg


set_context('green_thread')
h = create_host()
e1 = h.spawn('echo1', Echo)
e1.echo('hello there !!')
bot = h.spawn('bot', Bot)
bot2 = h.spawn('bot2', Bot)
bot.set_echo()
bot.ping(bot2)

sleep(3)

# ask = e1.raise_something(future=True)
ask = e1.say_something(future=True)
print 'Future: ', ask
sleep(0.1)
if ask.done():
    print 'Exception: ', ask.exception()
    try:
        print 'Result: ', ask.result(1)
    except Exception, e:
        print e

sleep(1)
h.shutdown()
