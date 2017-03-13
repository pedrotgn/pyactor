from pyactor.context import set_context, create_host, sleep
from pyactor.context import serve_forever, interval

from chord import Node


nodes = [1, 8, 14, 21, 32, 38, 42, 48, 51, 56, 128, 233]
nodes_h = {}

set_context()
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
    except Exception:
        continue
    interval(host, 1, nodes_h[i], "update")

interval(host, 30, nodes_h[0], "show")
sleep(1)
interval(host, 30, nodes_h[5], "show")
sleep(1)
interval(host, 30, nodes_h[9], "show")

serve_forever()
