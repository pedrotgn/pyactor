'''
Basic remote example sending ask messages. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host


class Echo:
    _tell = ['echo']
    _ask = ['get_msgs']

    def __init__(self):
        self.msgs = []

    def echo(self, msg):
        print msg
        self.msgs.append(msg)

    def get_msgs(self):
        return self.msgs


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')

    e1 = host.spawn('echo1', Echo)
    host.serve_forever()
