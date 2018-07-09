"""
Stress test. FUTURE
@author: Daniel Barcelona Pons
"""
import functools

from pyactor.context import set_context, create_host, shutdown, sleep, interval
from pyactor.exceptions import PyActorTimeoutError

from time import time

SERVERS = 5
CLIENTS = 20  # per server
INTERVALS = 50


class Connector(object):
    _tell = ['update', 'receive', 'init_start', 'set_server']
    _ref = ['set_server']

    def set_server(self, srvr):
        self.people = []
        self.server = srvr

    def init_start(self):
        self.cnt = 0
        self.interval = interval(self.host, 0.1, self.proxy, "update")

    def update(self):
        self.cnt += 1
        f = self.server.get_clients(future=True)
        f.add_callback("receive")
        # if self.cnt % 10 == 0:
        #     print self.id, self.cnt
        if self.cnt == INTERVALS:
            self.interval.set()
            self.server.remove_client(self.id)

    def receive(self, future):
        people = future.result()
        self.people = list(set(people) | set(self.people))


class Server(object):
    _tell = ['register_client', 'remove_client']
    _ask = ['get_clients', 'end']
    _ref = ['register_client', 'get_clients']

    def __init__(self):
        self.clients = {}

    def register_client(self, client):
        self.clients[client.get_id()] = client

    def get_clients(self):
        return self.clients.values()

    def remove_client(self, cli):
        del self.clients[cli]
        # print "stoped", cli
        if not self.clients.keys():
            print("Server", self.id, "ended.")

    def end(self):
        return not self.clients.keys()


if __name__ == "__main__":
    set_context('green_thread')
    host = create_host('http://127.0.0.1:1679/')

    clies = []
    servs = []

    for si in range(SERVERS):
        serv = host.spawn('s' + str(si), Server)
        servs.append(serv)
        for i in range(CLIENTS):
            c = host.spawn(str(si) + str(i), Connector)
            c.set_server(serv)
            serv.register_client(c)
            clies.append(c)
        print(si, 'online')

    print("All nodes created. Starting...")
    init = time()
    for node in clies:
        node.init_start()

    try:
        while not functools.reduce(lambda x, y: x and y.end(timeout=None),
                                   servs, True):
            sleep(0.01)

        end = time()

        print((end - init) * 1000, ' ms.')
    except PyActorTimeoutError:
        print("Timeout")
    shutdown()
