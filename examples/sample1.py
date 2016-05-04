'''
Basic host creation sample.
'''
from pyactor.context import create_host
from time import sleep

class Echo:
    _tell =['echo']
    _ask = []
    def echo(self,msg):
        print msg


h = create_host()
e1 = h.spawn('echo1',Echo)
e1.echo('from h: hello there !!')

hr = h.proxy
e2 = hr.spawn('echo2',Echo).get()
e2.echo('remote hello!!')

sleep(1)
h.shutdown()
