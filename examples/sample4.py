'''
Timeout sample.
'''
from pyactor.context import set_context, create_host, sleep, shutdown
from pyactor.exceptions import TimeoutError


class Echo(object):
    _tell = ['echo', 'bye']
    _ask = ['say_something']

    def echo(self, msg):
        print msg

    def bye(self):
        print 'bye'

    def say_something(self):
        sleep(2)
        return 'something'


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    e1.echo('hello there !!')
    e1.bye()

    try:
        x = e1.say_something(timeout=1)
    except TimeoutError:
        print 'timeout caught'
    sleep(1)
    shutdown()
