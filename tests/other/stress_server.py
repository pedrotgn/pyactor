"""
Stress test. SERVER
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, serve_forever


class Counter(object):
    _tell = ['work']
    _ask = ['see']

    def __init__(self):
        self.count = 1

    def work(self, num):
        chars = list(num)
        line = ''
        summ = 1
        for char in chars:
            line += char
            summ = summ * ord(char) / self.count
        print(line, summ)
        self.count = self.count + 1
        # print self.count

    def see(self):
        return self.count


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')
    c = host.spawn('worker', Counter)
    print('host listening at port 1277')

    serve_forever()
