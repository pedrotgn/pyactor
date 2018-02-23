'''
Testing comparation of proxies.
'''
from pyactor.context import set_context, create_host, sleep, serve_forever


class Echo(object):
    _tell = ['echo']
    _ask = []

    def echo(self, msg):
        print msg


def main():
    set_context()
    host = create_host('http://127.0.0.1:1277')
    p1 = host.spawn('1', Echo)
    p2 = host.lookup('1')

    print 'p1 =', id(p1)
    print 'p2 =', id(p2)

    print p1 == p2
    print p1 != p2
    print p1 is p2

    s = set()
    s.add(p1)
    s.add(p2)
    print len(s)

    print p1
    print repr(p1)

    serve_forever()


if __name__ == '__main__':
    main()
