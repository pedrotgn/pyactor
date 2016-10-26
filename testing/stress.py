'''
Stress test. CLIENTs
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, interval_host, \
        serve_forever
from pyactor.util import TimeoutError


CLIENTS = 100


class Connecter(object):
    _tell = ['send_message', 'init_start', 'set_server']
    _ref = ['set_server']

    def set_server(self, srvr):
        self.server = srvr

    def init_start(self):
        self.interval1 = interval_host(self.host, 0.1, self.send_message)

    def send_message(self):
        self.server.work('abcdefghijklmnopqrstuvwxyz' +
                         'abcdefghijklmnopqrstuvwxyz')
        # self.server.work(1)


class Show(object):
    _tell = ['send_message', 'init_start', 'set_server']
    _ref = ['set_server']

    def set_server(self, srvr):
        self.server = srvr

    def init_start(self):
        self.interval1 = interval_host(self.host, 1, self.send_message)

    def send_message(self):
        print self.server.see()


if __name__ == "__main__":
    set_context('green_thread')
    host = create_host('http://127.0.0.1:1679/')

    counter = host.lookup_url('http://127.0.0.1:1277/worker',
                              'Counter', 'stress_server')

    s = host.spawn('show', Show)
    s.set_server(counter)
    s.init_start()
    for i in xrange(CLIENTS):
        c = host.spawn(str(i), Connecter)
        c.set_server(counter)
        c.init_start()

    serve_forever()
