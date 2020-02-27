"""
Futures Sample.
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, sleep, shutdown


class Echo(object):
    _tell = {'echo'}
    _ask = {'say_something', 'raise_something'}

    def echo(self, msg):
        print(msg)

    def say_something(self):
        return "something"

    def raise_something(self):
        raise Exception("raising something")


if __name__ == '__main__':
    set_context()
    # set_context('green_thread')
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    e1.echo("hello there !!")

    # ask = e1.raise_something(future=True)
    ask = e1.say_something(future=True)
    print(f"Future: {ask}")
    sleep(0.1)
    if ask.done():
        print(f"Exception: {ask.exception()}")
        try:
            print(f"Result: {ask.result(1)}")
        except Exception as e:
            print(e)

    sleep(1)
    shutdown()
