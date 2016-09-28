'''
Remote example spawning on a remote server. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')

    print 'host listening at port 1277'

    host.serve_forever()
