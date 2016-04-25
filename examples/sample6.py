'''
lookup sample.
'''
from pyactor.context import init_host
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


h = init_host()
e1 = h.spawn('echo1',Echo).get()

e = h.lookup('echo1').get()
print e.say_something().get()

ee = h.lookup_url('local://local:6666/echo1', Echo).get()
print ee.say_something().get()

sleep(1)
h.shutdown()
