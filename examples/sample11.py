"""
Intervals sample
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, sleep, shutdown, \
    interval, later


class Registry(object):
    _ask = []
    _tell = ["hello", "init_start", "stop_interval"]
    # _ref = ['hello']

    def init_start(self):
        self.interval1 = interval(self.host, 1, self.proxy, "hello", "you", ",,")
        later(5, self.proxy, "stop_interval")

    def stop_interval(self):
        print("stopping interval")
        self.interval1.set()

    def hello(self, msg, m2):
        print(f"{self.id} Hello {msg} {m2}")


if __name__ == "__main__":
    N = 2   # 10000

    set_context()
    host = create_host()
    registry = list()
    for i in range(0, N):
        registry.append(host.spawn(str(i), Registry))

    for i in range(0, N):
        registry[i].init_start()

    sleep(8)
    shutdown()
