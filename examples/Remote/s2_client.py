"""
Basic remote example sending ask messages. CLIENT
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, shutdown


if __name__ == '__main__':
    set_context()
    host = create_host("http://127.0.0.1:1679")

    e1 = host.lookup_url("http://127.0.0.1:1277/echo1", 'Echo', 's2_server')

    e1.echo('Hi there!')    # TELL message
    e1.echo('See ya!')

    print(e1.get_msgs())

    shutdown()
