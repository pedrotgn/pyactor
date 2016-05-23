'''
Parallel methods sample.
'''
from pyactor.context import create_host
from pyactor.util import Timeout
from time import sleep


class File(object):
    _ask = ['download']
    _tell = []
    _parallel = []
    _ref = []

    def download(self,filename):
        print 'downloading '+ filename
        sleep(5)
        return True

class Web(object):
    _ask = ['list_files','get_file']
    _tell = ['remote_server']
    #_parallel = ['get_file']  # Comment this line to check the raise of timeouts if paral are not used.
    _ref = ["remote_server"]

    def __init__(self):
        self.files = ['a1.txt','a2.txt','a3.txt','a4.zip']
    def remote_server(self, file_server):
        self.server = file_server
    def list_files(self):
        return self.files
    def get_file(self,filename):
        return self.server.download(filename).get(10)

class Workload(object):
    _ask = []
    _tell = ['launch','download', 'remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        for i in range(10):
            try:
                print self.server.list_files().get(2)
            except Timeout as e:
                print "timeout"

    def remote_server(self, web_server):
        self.server = web_server

    def download(self):

        self.server.get_file('a1.txt').get(10)
        print 'download finished'



host = create_host()

f1 = host.spawn('file1', File)
web = host.spawn('web1', Web)
web.remote_server(f1)
load = host.spawn('wl1', Workload)
load.remote_server(web)
load2 = host.spawn('wl2', Workload)
load2.remote_server(web)
load.launch()
load2.download()

sleep(10)
host.shutdown()
#host.serve_forever()
