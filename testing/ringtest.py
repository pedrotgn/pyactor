'''
RING test. Messages per second. Number of nodes.
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, sleep, shutdown

from time import time


NUM_NODES = 10000
NUM_MSGS = 100


class Node(object):
    _tell = ['set_next', 'init_token', 'take_token']
    _ask = ['get_cnt', 'is_finished']
    _ref = ['set_next']

    def __init__(self, next=None):
        self.next = next
        self.cnt = 0

    def set_next(self, next_node):
        self.next = next_node

    def get_cnt(self):
        return self.cnt

    def is_finished(self):
        return self.cnt >= NUM_MSGS

    def init_token(self):
        self.next.take_token()

    def take_token(self):
        self.cnt += 1
        if (not self.is_finished()):
            self.next.take_token()


if __name__ == "__main__":
    set_context('green_thread')
    # set_context('thread')

    print 'TEST ', NUM_NODES, ' nodes and', NUM_MSGS, "messages."

    host = create_host()

    nf = host.spawn('ini', Node)

    ni = nf
    for i in range(NUM_NODES - 2):
        ni = host.spawn(str(i), Node, [ni])

    n1 = host.spawn('end', Node, [ni])

    nf.set_next(n1)
    print 'start time!!'
    init = time()

    nf.init_token()

    while (not n1.is_finished()):
        sleep(0.01)

    end = time()

    print ((end - init) * 1000), ' ms.'

    shutdown()
