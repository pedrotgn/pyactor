from pyactor.context import set_context, create_host, sleep, interval_host,\
    serve_forever
from pyactor.util import AlreadyExistsError

from chord import show, update, Node, k

from time import time
import random


def mhash(line):
    import sha
    key = long(sha.new(line).hexdigest(), 16)
    return key


def cid():
    return long(random.uniform(0, 2**k))


nodes_h = {}

set_context('green_thread')
host = create_host()

t1 = time()
# Create and initialize nodes
for i in range(100):
    while True:
        try:
            nodes_h[i] = host.spawn(str(cid()), Node)
        except AlreadyExistsError:
            continue
        break
    # print nodes_h[i].get_id()
    nodes_h[i].init_node()

for i in range(len(nodes_h)):
    j = 0 if i is 0 else i-1
    try:
        if nodes_h[i].join(nodes_h[j], timeout=20):
            print 'JOIN OK', nodes_h[i].get_id()
        else:
            print 'Node %s fails' % str(i)
    except Exception:
        continue
    interval_host(host, 0.5, update, nodes_h[i])

t2 = time()
print 'Time to create 100 nodes'
print t2 - t1

interval_host(host, 30, show, nodes_h[0])
sleep(1)
interval_host(host, 30, show, nodes_h[5])
sleep(1)
interval_host(host, 30, show, nodes_h[9])

# Wait to give time to chord to fix its tables.
sleep(60)

key = mhash('hello')
print key
print key % 2**k
show(nodes_h[0])
found = nodes_h[0].find_predecessor(key % 2**k, timeout=30)
print found.get_id()


serve_forever()
