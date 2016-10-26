from pyactor.context import set_context, create_host, Host, sleep, shutdown


class EchoC(object):
    _tell = ['echo', 'set_callback', 'echoc']
    _ask = []

    def set_callback(self, future):
        future.add_callback('echo')

    def echo(self, future):
        msg = future.result(4)
        print msg, 'From callback!'

    def echoc(self, msg):
        print msg


if __name__ == "__main__":
    set_context('green_thread')
    host = create_host('http://127.0.0.1:1679')

    spk = host.spawn('echo', EchoC)

    e1 = host.lookup_url('http://127.0.0.1:1277/echo1', 'Echo', 'server')
    # print e1
    h = host.lookup_url('http://127.0.0.1:1277/', Host)
    # print h

    e1.echo('HEY!')    # TELL message

    h.hello()
    print h.say_hello(timeout=1), 'ASK message!'      # ASK Message

    f = h.say_hello(future=True)
    e1.set_c(spk)
    # e1.set_c(f)
    # f.add_callback('echoc', e1)
    print f.result(2), 'Future!'
    # sleep(1)
    # spk.set_callback(f)

    sleep(4)
    shutdown()
