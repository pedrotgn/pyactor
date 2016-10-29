'''
Stopping an actor.
'''
from pyactor.context import set_context, create_host, sleep, shutdown


class Echo(object):
    _tell = ['echo']
    _ask = []

    def echo(self, msg):
        print msg


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    e1.echo('hello there !!')

    sleep(1)
    h.stop_actor('echo1')

    e1 = h.spawn('echo1', Echo)
    e1.echo('hello there !!')

    sleep(1)
    shutdown()
