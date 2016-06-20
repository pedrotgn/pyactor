'''
Multiple hosts.
'''
from pyactor.context import set_context(), create_host, sleep


class Echo:
    _tell = ['echo']
    _ask = []
    _ref = ['echo']

    def echo(self, msg, pref):
        print msg, pref


set_context()
h = create_host()
e1 = h.spawn('echo1', Echo)
e1.echo('hello there !!', e1)
print e1

h2 = create_host("local://local:7777/host")
e2 = h2.spawn('echo1', Echo)
e2.echo('hello 2', e1)
print e2

sleep(1)

try:
    e1.echo('hello 3', e2)  # This line raises TCPthing
    e2.echo('hello 2', e2)  # This one also
except Exception, e:
    print e

sleep(1)
h.shutdown()
h2.shutdown()
