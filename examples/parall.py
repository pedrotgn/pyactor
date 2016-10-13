'''
More simple Parallel methods sample.
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, sleep
from pyactor.util import TimeoutError


class Work(object):
    _ask = ['sleeping']

    def sleeping(self, t):
        sleep(t)
        return True


class ParaWork(object):
    _tell = ['work']
    _ask = ['check_work']
    _parallel = ['work']

    def __init__(self):
        self.count = 0

    def work(self):
        sl = self.host.spawn('sl', Work)
        for i in xrange(5):
            print 'working', i
            sl.sleeping(1, timeout=2)
            self.count += 1
        # return True

    def check_work(self):
        return self.count


if __name__ == "__main__":
    # set_context('green_thread')
    set_context()

    host = create_host()
    worker = host.spawn('w1', ParaWork)

    try:
        worker.work()
    except TimeoutError, e:
        print e

    for i in xrange(5):
        try:
            print worker.check_work(timeout=None)
            sleep(1)
        except TimeoutError, e:
            print e

    sleep(7)
    host.shutdown()
