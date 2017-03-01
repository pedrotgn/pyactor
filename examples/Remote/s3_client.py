'''
Remote example spawning on a remote server. CLIENT
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, Host, sleep, shutdown
from pyactor.exceptions import TimeoutError


class Server(object):
    _ask = {'add', 'wait_a_lot'}
    _tell = ['substract']

    def add(self, x, y):
        return x + y

    def substract(self, x, y):
        print 'subtract', x - y

    def wait_a_lot(self):
        sleep(2)
        return 'ok'


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1679')

    remote_host = host.lookup_url('http://127.0.0.1:1277/', Host)
    print remote_host
    server = remote_host.spawn('server', 's3_client/Server')
    z = server.add(6, 7)
    print z
    server.substract(6, 5)
    t = server.add(8, 7)
    print t

    try:
        print server.wait_a_lot(timeout=1)
    except TimeoutError, e:
        print e

    sleep(3)
    shutdown()
