"""
Basic remote example sending tell messages. CLIENT
@author: Daniel Barcelona Pons
"""
from pyactor.context import \
    set_context, create_host, set_rabbit_credentials, shutdown


if __name__ == '__main__':
    set_rabbit_credentials('daniel', 'passs')
    set_context()
    host = create_host("amqp://127.0.0.1:1679")

    e1 = host.lookup_url("amqp://127.0.0.1:1277/echo1", 'Echo', 's1_server')

    e1.echo("Hi there!")    # TELL message
    e1.echo("See ya!")

    shutdown()
