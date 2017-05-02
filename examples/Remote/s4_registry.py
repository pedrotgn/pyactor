'''
Remote example with a registry. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, serve_forever


class NotFound(Exception):
    pass


class Registry(object):
    _ask = ['get_all', 'bind', 'lookup', 'unbind']
    _async = []
    _ref = ['get_all', 'bind', 'lookup']

    def __init__(self):
        self.actors = {}

    def bind(self, name, actor):
        print "server registred", name
        self.actors[name] = actor

    def unbind(self, name):
        if name in self.actors.keys():
            del self.actors[name]
        else:
            raise NotFound()

    def lookup(self, name):
        if name in self.actors:
            return self.actors[name]
        else:
            return None

    def get_all(self):
        return self.actors.values()


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:6000/')

    registry = host.spawn('regis', Registry)

    print 'host listening at port 6000'

    serve_forever()
