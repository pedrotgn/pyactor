'''
Basic remote example sending tell messages. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host


class Echo(object):
    _tell = ['echo']
    _ask = []

    def echo(self, msg):
        print msg

if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')

    e1 = host.spawn('echo1', Echo)
    host.serve_forever()
