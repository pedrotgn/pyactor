'''
Multiple hosts.
'''
from pyactor.context import set_context, create_host, sleep


class Echo(object):
    _tell = ['echo']
    _ask = []
    _ref = ['echo']

    def echo(self, msg, pref=None):
        print msg, pref


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    e1.echo('hello there !!', e1)
    # With non http servers, only proxies from the same server can be passed
    # as parameter.
    # print e1

    h2 = create_host("local://local:7777/host")
    # print h2
    e2 = h2.spawn('echo1', Echo)
    e2.echo('hello 2')
    # Here we can't pass the e1 proxy (would raise exception).
    # print e2

    sleep(1)

    try:
        e1.echo('hello 3', e2)  # This line raises ERROR in lookup
    except Exception, e:
        print e

    sleep(1)
    h.shutdown()
    h2.shutdown()
