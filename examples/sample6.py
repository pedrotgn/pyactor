'''
Self references sample. Actor id/proxy. + serve_forever
'''
from pyactor.context import set_context, create_host, sleep, serve_forever


class Echo(object):
    _tell = ['echo']
    _ask = []

    def echo(self, msg, sender):
        print msg, 'from:', sender.get_name(), 'at', sender.get_net()
        # print sender.get_id(), sender.get_url()


class Bot(object):
    _tell = ['set_echo', 'say_hi']
    _ask = ['get_name', 'get_net']

    def __init__(self):
        self.greetings = ['hello', 'hi', 'hey', 'what`s up?']

    def set_echo(self):
        self.echo = self.host.lookup('echo1')

    def get_name(self):
        return self.id

    def get_net(self):
        return self.url

    def say_hi(self):
        for salute in self.greetings:
            self.echo.echo(salute, self.proxy)


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    bot = h.spawn('bot1', Bot)
    bot.set_echo()
    bot.say_hi()

    sleep(1)
    serve_forever()
