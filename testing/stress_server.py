'''
Stress test. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host

class Counter(object):
    _tell = ['add', 'see']

    def __init__(self):
        self.count = 0

    def add(self, num):
        self.count += num

    def see(self):
        print self.count
        

if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')
    c = host.spawn('worker', Counter)
    print 'host listening at port 1277'

    host.serve_forever()
