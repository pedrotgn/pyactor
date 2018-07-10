from pyactor.context import set_context, create_host, shutdown, Host


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1679')

    rhost = host.lookup_url('http://127.0.0.1:1277/', Host)

    e1 = host.lookup_url('http://127.0.0.1:1277/echo1', 'Echo', 'stopserver')

    rhost.stop_actor('echo1')

    # e1.echo('Hi there!')    # TELL message
    # e1.echo('See ya!')
    try:
        print e1.ret('hi')
    except Exception, e:
        print e

    shutdown()
