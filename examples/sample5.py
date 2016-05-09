'''
Lookup sample.
'''
from pyactor.context import create_host
from time import sleep

class Echo:
    _tell =['echo','bye']
    _ask = ['say_something']
    def echo(self,msg):
        print msg
    def bye(self):
        print 'bye'
    def say_something(self):
        return 'something'


h = create_host()
e1 = h.spawn('echo1',Echo)

e = h.lookup('echo1')
print e.say_something().get()

ee = h.lookup_url('local://local:6666/echo1', Echo)
print ee.say_something().get()

'''eg = h.spawn_n(3,'echog',Echo)
eg.echo('hello')'''

sleep(1)
h.shutdown()
