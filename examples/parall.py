"""
More simple Parallel methods sample.
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, sleep, shutdown
from pyactor.exceptions import PyActorTimeoutError


class Work(object):
    _ask = ["sleeping"]

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
        for i in range(5):
            print(f"working {i}")
            sl.sleeping(2, timeout=3)
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
    except PyActorTimeoutError as e:
        print(e)

    for i in range(10):
        try:
            print(worker.check_work(timeout=None))
            sleep(1)
        except PyActorTimeoutError as e:
            print(e)

    sleep(2)
    shutdown()
