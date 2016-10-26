'''
Lookup sample.
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
        return 'something'


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)

    e = h.lookup('echo1')
    print e.say_something()

    ee = h.lookup_url('local://local:6666/echo1', Echo)
    print ee.say_something()

    sleep(1)
    shutdown()
