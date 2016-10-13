from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import cPickle
import xmlrpclib
import threading


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ()


class Source(threading.Thread):
    ''' Facade for simle remote communication using XMLRPCServer.
    '''
    def __init__(self, addr):
        threading.Thread.__init__(self)
        ip, port = addr
        self.addr = addr

        self.server = SimpleXMLRPCServer((ip, port),
                                         requestHandler=RequestHandler,
                                         logRequests=False,
                                         allow_none=True)
        # self.server.register_introspection_functions()

    def register_function(self, func):
        self.server.register_function(func, 'send')

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class Sink(object):
    ''' Facade for XMLRPC proxies.
    '''
    def __init__(self, url):
        self.endpoint = xmlrpclib.ServerProxy(url)

    def send(self, msg):
        msg = cPickle.dumps(msg)
        return self.endpoint.send(msg)
