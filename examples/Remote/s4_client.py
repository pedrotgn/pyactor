'''
Remote example with registry. CLIENT
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1679')

    registry = host.lookup_url('http://127.0.0.1:1277/regis', 'Registry',
                               's4_registry')

    registry.bind('host1', host.proxy)

    host.serve_forever()
