'''
Basic host creation sample.
'''
from pyactor.context import set_context, create_host, sleep


class Echo(object):
    _tell = ['echo']
    _ask = []

    def echo(self, msg):
        print msg

set_context()
h = create_host()
e1 = h.spawn('echo1', Echo)
e1.echo('hello there !!')

hr = h.proxy
e2 = hr.spawn('echo2', Echo)
e2.echo('remote hello!!')

sleep(1)
h.shutdown()
