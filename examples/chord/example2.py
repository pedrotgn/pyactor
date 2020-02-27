from pyactor.context import set_context, create_host, sleep, serve_forever, \
    interval
from pyactor.exceptions import AlreadyExistsError

from chord import Node, k

from time import time
import random


def mhash(line):
    import hashlib
    return int(hashlib.sha1(line.encode('utf-8')).hexdigest(), 16)


def cid():
    return int(random.uniform(0, 2**k))


nodes_h = {}

if __name__ == '__main__':

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
                print("JOIN OK", nodes_h[i].get_id())
            else:
                print('Node %s fails' % str(i))
        except Exception:
            continue
        interval(host, 0.5, nodes_h[i], "update")

    t2 = time()
    print("Time to create 100 nodes")
    print(t2 - t1)

    interval(host, 30, nodes_h[0], "show")
    sleep(1)
    interval(host, 30, nodes_h[5], "show")
    sleep(1)
    interval(host, 30, nodes_h[9], "show")

    # Wait to give time to chord to fix its tables.
    sleep(60)

    key = mhash('hello')
    print(key)
    print(key % 2 ** k)
    nodes_h[0].show()
    found = nodes_h[0].find_predecessor(key % 2**k, timeout=30)
    print(found.get_id())

    serve_forever()
