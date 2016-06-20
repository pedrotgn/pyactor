from gevent.event import Event
from gevent import getcurrent
import gevent


def sleep(seconds):
    gevent.sleep(seconds)


def later(timeout, f, *args, **kwargs):
    '''
    Sets a timer that will call the *f* function past *timeout* seconds.
    See example in :ref:`sample_inter`

    :return: :class:`Greenlet`
    '''
    def wrap(*args, **kwargs):
        sleep(timeout)
        return f(*args, **kwargs)

    return gevent.spawn(wrap, *args, **kwargs)


def interval_host(host, time, f, *args, **kwargs):
    '''
    Creates an Event attached to the *host* that will execute the *f*
    function every *time* seconds.

    See example in :ref:`sample_inter`

    :param Proxy host: proxy of the host. Can be obtained from inside a
        class with ``self.host``.
    :param int time: seconds for the intervals.
    :param func f: function to be called every *time* seconds.
    :param list args: arguments for *f*.
    :return: :class:`Event` instance of the interval.
    '''
    def wrap(*args, **kwargs):
        thread = getcurrent()
        args = list(args)
        stop_event = args[0]
        del args[0]
        args = tuple(args)
        while not stop_event.is_set():
            f(*args, **kwargs)
            stop_event.wait(time)
        host.detach_interval(thread)
    t2_stop = Event()
    args = list(args)
    args.insert(0, t2_stop)
    args = tuple(args)
    t = gevent.spawn(wrap, *args, **kwargs)
    thread_id = t
    host.attach_interval(thread_id, t2_stop)
    return t2_stop
