from pyactor.context import set_context, create_host, sleep


class Echo:
    _tell = ['echo']
    _ask = []

    def echo(self, msg):
        print msg, self.id


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/host')

    e1 = host.spawn('echo1', Echo)
    host.serve_forever()
