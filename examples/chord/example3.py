from pyactor.context import set_context, create_host, sleep, serve_forever

from chord import Node


nodes = [1, 8, 14, 21, 32, 38, 42, 48, 51, 56]
nodes_h = {}

set_context('green_thread')
host = create_host()

# Create and initialize nodes
for i in range(len(nodes)):
    nodes_h[i] = host.spawn(str(nodes[i]), Node)
    nodes_h[i].init_node()

for i in range(len(nodes_h)):
    j = 0 if i is 0 else i-1
    try:
        if nodes_h[i].join(nodes_h[j], timeout=20):
            print 'JOIN OK', nodes_h[i].get_id()
        else:
            print 'Node %s fails' % str(i)
    except Exception:
        raise
    else:
        host.interval(0.5, nodes_h[i], "update")

# Wait to give time to chord to fix its tables.
sleep(5)

found = nodes_h[0].find_successor(40)
print 'found', found.get_id()


serve_forever()
