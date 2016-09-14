'''
Parallel methods sample. With Futures.
'''
from pyactor.context import set_context, create_host, sleep
from pyactor.util import TimeoutError


class File(object):
    _ask = ['download']

    def download(self, filename):
        print 'downloading ' + filename
        sleep(5)
        return True


class Web(object):
    _ask = ['list_files', 'get_file']
    _tell = ['remote_server']
    _parallel = ['list_files', 'get_file', 'remote_server']
# Comment the line above to check the raise of timeouts if paral are not used.
    _ref = ["remote_server"]

    def __init__(self):
        self.files = ['a1.txt', 'a2.txt', 'a3.txt', 'a4.zip']

    def remote_server(self, file_server):
        self.server = file_server

    def list_files(self):
        return self.files

    def get_file(self, filename):
        future = self.server.download(filename, future=True)
        return future.result(6)


class Workload(object):
    _ask = []
    _tell = ['launch', 'download', 'remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        for i in range(10):
            try:
                print self.server.list_files(timeout=2)
            except TimeoutError as e:
                print i, e

    def remote_server(self, web_server):
        self.server = web_server

    def download(self):
        self.server.get_file('a1.txt', timeout=10)
        print 'download finished'


if __name__ == "__main__":
    set_context('green_thread')
    # set_context()

    host = create_host()

    f1 = host.spawn('file1', File)
    web = host.spawn('web1', Web)
    sleep(1)
    web.remote_server(f1)
    load = host.spawn('wl1', Workload)
    load.remote_server(web)
    load2 = host.spawn('wl2', Workload)
    load2.remote_server(web)

    load.launch()
    load2.download()

    sleep(7)
    print host.pthreads
    # print host.threads
    host.shutdown()
