from pyactor.context import set_context, create_host, serve_forever


class Echo(object):
    _tell = ['echo', 'set_c', 'echoc']
    _ask = []
    _ref = ['set_c']

    def echo(self, msg):
        print msg, self.id

    def set_c(self, future):
        print 'sending to another'
        # print future
        future.echoc('something')
        # print future.result(2)
        # future.add_callback('echoc')

    def echoc(self, future):
        print future.result(2), 'callback'


if __name__ == "__main__":
    set_context('green_thread')
    host = create_host('http://127.0.0.1:1277/')

    e1 = host.spawn('echo1', Echo)
    serve_forever()
