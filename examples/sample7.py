"""
Proxy references by parameter sample.
"""
from pyactor.context import set_context, create_host, sleep, shutdown


class Echo(object):
    _tell = {'echo', 'echo2', 'echo3'}
    _ref = {'echo', 'echo2', 'echo3'}

    def echo(self, msg, sender):
        print(f"{msg} from: {sender.get_name()}")

    def echo2(self, msg, senders):
        for sender in senders:
            print(f"{msg} from: {sender.get_name()}")

    def echo3(self, msg, senders):
        for sender in senders.values():
            print(f"{msg} from: {sender.get_name()}")


class Bot(object):
    _tell = {'set_echo', 'say_hi'}
    _ask = {'get_name'}
    _ref = {'set_echo'}

    def __init__(self):
        self.greetings = ["hello", "hi", "hey", "what's up?"]

    def set_echo(self, echo):
        self.echo = echo

    def get_name(self):
        return self.id

    def say_hi(self):
        for salute in self.greetings:
            self.echo.echo(salute, self.proxy)


if __name__ == '__main__':
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    bot = h.spawn('bot1', Bot)
    bot2 = h.spawn('bot2', Bot)
    bot.set_echo(e1)    # Passing a proxy to a method marked as _ref
    sleep(1)            # Give time to host to lookup the first one
    bot2.set_echo(e1)
    bot.say_hi()
    sleep(1)
    e1.echo2("hello there!", [bot2])
    e1.echo3("hello there!!", {'bot1': bot, 'bot2': bot2})

    sleep(1)
    shutdown()
