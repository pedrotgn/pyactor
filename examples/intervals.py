from pyactor.context import create_host
from pyactor.intervals import interval_host, later


class Registry():
    _ask = []
    _tell = ['hello', 'init_start']

    def init_start(self):
        self.interval1 = interval_host(self.host, 1, self.hello)
        later(10, self.stop_interval)

    def stop_interval(self):
        self.interval1.set()

    def hello(self):
        print 'Hello'


host = create_host()
registry = host.spawn('1', Registry)
registry.init_start()
host.serve_forever()
