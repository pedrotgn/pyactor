'''
Self references sample. Actor id/proxy
'''
from pyactor.context import init_host
from time import sleep
from pyactor.util import Timeout

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
print e1.id
e1.echo('hola amigo !!')
e1.bye()
sleep(1)
e2 = e1.get_proxy()
print e2.id
print e2.say_something().get()

sleep(1)
h.shutdown()
