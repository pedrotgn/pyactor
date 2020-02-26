import time as timep
from threading import Thread, Timer, Event


def sleep(time):
    """
    Facade for the sleep function. Avoid using time.sleep.

    :param  int time: time to sleep, in seconds. (Float for second
        divisions)
    """
    timep.sleep(time)


def later(timeout, f, *args, **kwargs):
    """
    Sets a timer that will call the *f* function past *timeout* seconds.

    See example in :ref:`sample_inter`

    :return: :class:`Timer`
    """
    if kwargs is None:
        kwargs = {}
    if args is None:
        args = []
    t = Timer(timeout, f, args, kwargs)
    t.start()
    return t


def interval_host(host, time, f, *args, **kwargs):
    """
    Creates an Event attached to the *host* that will execute the *f*
    function every *time* seconds.

    See example in :ref:`sample_inter`

    :param Proxy host: host proxy. Can be obtained from inside a
        class with ``self.host``.
    :param int time: seconds for the intervals.
    :param func f: function to be called every *time* seconds.
    :param list args: arguments for *f*.
    :return: :class:`Event` instance of the interval.
    """
    def wrap(*args, **kwargs):
        # thread = currentThread()
        args = list(args)
        stop_event = args[0]
        del args[0]
        args = tuple(args)
        while not stop_event.is_set():
            f(*args, **kwargs)
            stop_event.wait(time)
        host.detach_interval(thread_id)

    t2_stop = Event()
    args = list(args)
    args.insert(0, t2_stop)
    args = tuple(args)
    t = Thread(target=wrap, args=args, kwargs=kwargs)
    t.start()
    thread_id = t.getName()
    host.attach_interval(thread_id, t2_stop)
    return t2_stop
