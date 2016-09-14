from pyactor.context import set_context, create_host, Host

# class Echo:
#     _tell =['echo']
#     _ask = []
#     def echo(self,msg):
#         print msg, self.id


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1679')

    e1 = host.lookup_url('http://127.0.0.1:1277/echo1', 'Echo', 'server')
    # print e1
    h = host.lookup_url('http://127.0.0.1:1277/host', Host)
    # print h
    h.hello()
    print h.say_hello(timeout=None)
    e1.echo('Daniel es grande!')
    host.shutdown()

    # e1 = h.spawn('echo1',Echo).get()
