'''
Proxy references by parameter sample.
'''
from pyactor.context import set_context, create_host, sleep, shutdown


class Echo(object):
    _tell = ['echo', 'echo2', 'echo3']
    _ask = []
    _ref = ['echo', 'echo2', 'echo3']

    def echo(self, msg, sender):
        # print sender
        print msg, 'from:', sender.get_name()

    def echo2(self, msg, sndrs):
        for sender in sndrs:
            print msg, 'from:', sender.get_name()

    def echo3(self, msg, sndrs):
        for sender in sndrs.values():
            print msg, 'from:', sender.get_name()

class Bot(object):
    _ask = ['get_name']

    def get_name(self):
        return self.id


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    bot = h.spawn('bot1', Bot)
    bot2 = h.spawn('bot2', Bot)
    sleep(1)
    e1.echo('HI!', bot)
    e1.echo2('hello there!', [bot2])
    e1.echo3('hello there!!', {'bot1': bot, 'bot2': bot2})

    sleep(1)
    shutdown()
