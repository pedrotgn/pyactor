from pyactor.context import set_context, create_host, sleep, interval_host

from chord import show, update, Node


nodes = [1, 8, 14, 21, 32, 38, 42, 48, 51, 56]
nodes_h = {}

set_context('green_thread')
host = create_host()

# Create and initialize nodes
for i in range(len(nodes)):
    print 'iteration', i
    nodes_h[i] = host.spawn(str(nodes[i]), Node)
    nodes_h[i].init_node()

for i in range(len(nodes)):
    j = 0 if i is 0 else i-1
    try:
        if nodes_h[i].join(nodes_h[j], timeout=20):
            print 'JOIN OK', str(i)
        else:
            print 'Node %s fails' % str(i)
    except:
        raise
    else:
        pass
        interval_host(host, 1, update, nodes_h[i])

interval_host(host, 30, show, nodes_h[0])
sleep(1)
interval_host(host, 30, show, nodes_h[5])
sleep(1)
interval_host(host, 30, show, nodes_h[9])

host.serve_forever()
