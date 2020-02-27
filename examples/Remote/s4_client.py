"""
Remote example with registry. CLIENT
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, serve_forever


if __name__ == '__main__':
    set_context()
    host = create_host("http://127.0.0.1:6001")

    registry = host.lookup_url("http://127.0.0.1:6000/regis", 'Registry',
                               's4_registry')

    registry.bind('host1', host)

    serve_forever()
