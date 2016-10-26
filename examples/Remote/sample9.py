'''
Multiple hosts. Remote requiered since v0.9.
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, sleep, shutdown


class Echo(object):
    _tell = ['echo']
    _ask = []
    _ref = ['echo']

    def echo(self, msg, pref=None):
        print msg, pref


if __name__ == "__main__":
    set_context()
    h = create_host("http://127.0.0.1:6666/host")
    e1 = h.spawn('echo1', Echo)
    e1.echo('hello there !!', e1)

    h2 = create_host("http://127.0.0.1:7777/host")
    e2 = h2.spawn('echo1', Echo)
    e2.echo('hello 2', e1)

    sleep(1)

    e1.echo('hello 3', e2)

    sleep(1)
    shutdown()
    # or, to only stop one of them:
    # shutdown("http://127.0.0.1:7777/host")
