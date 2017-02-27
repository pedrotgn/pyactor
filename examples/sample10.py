'''
Intervals sample
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, sleep, shutdown


class Registry(object):
    _ask = []
    _tell = ['hello', 'init_start', 'stop_interval']
    # _ref = ['hello']

    def init_start(self):
        self.interval1 = self.host.interval(1, self.proxy, "hello", "you")
        self.host.later(10, self.proxy, "stop_interval")

    def stop_interval(self):
        print "stopping interval"
        self.interval1.set()

    def hello(self, msg):
        print 'Hello', msg


if __name__ == "__main__":
    set_context()
    host = create_host()
    registry = host.spawn('1', Registry)
    registry.init_start()

    sleep(11)
    shutdown()
