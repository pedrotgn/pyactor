from pyactor.context import set_context, create_host, sleep, shutdown


class Consum(object):
    _tell = ['say_hi']
    _ask = ['get_proxies']
    _ref = ['get_proxies']
    # _parallel = ['get_proxies']

    def say_hi(self):
        print('hi', self.id)

    def get_proxies(self, db):
        future = db.get_proxies(future=True)
        # future.add_callback('read_future', db)
        print(future.result())
        return future
        # while not future.done:
        #     sleep(0.1)
        # proxies = future.result()
        # return proxies


if __name__ == "__main__":
    set_context()
    h = create_host('http://127.0.0.1:1679')
    # db = h.spawn('db', DB)
    c = h.spawn('c', Consum)
    # p1 = h.spawn('p1', Consum)
    # p2 = h.spawn('p2', Consum)

    db = h.lookup_url('http://127.0.0.1:1277/db', 'DB', 'ffutureref')

    # db.set_proxies(p1, p2)
    try:
        result = c.get_proxies(db)
        print(result.result())
    # db.read_future(result)
    except Exception as e:
        print(e)

    sleep(1)
    shutdown()
