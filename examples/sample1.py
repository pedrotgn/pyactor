'''
Basic host creation sample.
'''
from pyactor.context import init_host
from time import sleep

class Echo:
    _tell =['echo']
    _ask = []
    def echo(self,msg):
        print msg


h = init_host()
e1 = h.spawn('echo1',Echo).get()
e1.echo('hello there !!')
sleep(1)
h.shutdown()
