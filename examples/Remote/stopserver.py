from pyactor.context import set_context, create_host, serve_forever


class Echo(object):
    _tell = ['echo']
    _ask = ['ret']

    def echo(self, msg):
        print msg

    def ret(self, msg):
        return msg


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')

    e1 = host.spawn('echo1', Echo)
    serve_forever()
