from pyactor.context import set_context, create_host, sleep, shutdown,\
    serve_forever


class DB(object):
    _tell = ['set_proxies', 'read_future']
    _ask = ['get_proxies']
    _ref = ['set_proxies', 'get_proxies']

    def __init__(self):
        self.proxies = []

    def set_proxies(self, p1, p2):
        self.proxies.append(p1)
        self.proxies.append(p2)
        # print self.proxies

    def get_proxies(self):
        return self.proxies
        sleep(5)
        return 'hi'

    def read_future(self, future):
        print future.result()


if __name__ == "__main__":
    set_context()
    h = create_host('http://127.0.0.1:1277')
    db = h.spawn('db', DB)
    # c = h.spawn('c', Consum)
    p1 = h.spawn('p1', DB)
    p2 = h.spawn('p2', DB)

    db.set_proxies(p1, p2)
    # result = c.get_proxies(db)
    # print result

    # sleep(1)
    serve_forever()
