from pyactor.context import init_host,serve_forever



class Echo:
    _tell =['echo']
    _ask = []
    def echo(self,msg):
        print msg,self.id


tcpconf = ('tcp',('127.0.0.1',1265))
host = init_host('server',tcpconf)

e1 = host.spawn('echo1',Echo).get()

serve_forever()
