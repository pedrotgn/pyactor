from pyactor.context import set_context, create_host, sleep, shutdown,\
    serve_forever


class Someclass(object):
    _tell = ['show_things']

    def __init__(self, op, thing):
        self.things = [op, thing]

    def show_things(self):
        print self.things


if __name__ == "__main__":
    set_context()
    h = create_host()

    params = ["hi", "you"]
    # kparams = {"op":"hi", "thing":"you"}

    # t = h.spawn('t', Someclass, *params)
    t = h.spawn('t', Someclass, *["hi", "you"])

    t.show_things()

    shutdown()
