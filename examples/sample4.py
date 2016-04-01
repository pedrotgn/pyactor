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
        sleep(2)
        return 'something'




h = init_host()
e1 = h.spawn('echo1',Echo).get()
e1.echo('hola amigo !!')
e1.bye()

try:
    x = e1.say_something().get(1)
except Timeout:
    print 'timeout catched'
sleep(1)
h.shutdown()
