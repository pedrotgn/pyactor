'''
Multiple hosts.
'''
from pyactor.context import create_host

from time import sleep


class Echo:
    _tell = ['echo']
    _ask = []
    _ref = ['echo']

    def echo(self, msg, pref):
        print msg, pref


h = create_host()
e1 = h.spawn('echo1', Echo)
e1.echo('hello there !!', e1)
print e1

h2 = create_host("local://local:7777/host")
e2 = h2.spawn('echo1', Echo)
e2.echo('hello 2', e1)
print e2

e1.echo('hello 3', e2)  # This line raises TCPthing

sleep(1)
h.shutdown()
h2.shutdown()
