from pyactor.context import init_host


class Echo:
    _tell =['echo']
    _ask = []
    def echo(self,msg):
        print msg,self.id

tcpconf = ('tcp',('127.0.0.1',1668))
host = init_host('tcp://127.0.0.1:1679')

e1 = host.lookup_url('tcp://127.0.0.1:1277/echo1',Echo).get()
e1.echo('pedro es grande!')
host.shutdown()


#e1 = h.spawn('echo1',Echo).get()
