from threading import Thread, Timer, Event, currentThread
import time as timep

def later(timeout,f,*args, **kwargs):
    t = Timer(timeout, f, args)
    t.start()
    return t


def interval_host(host, time, f, *args, **kwargs):
    def wrap(*args, **kwargs):
        thread = currentThread()
        thread.getName()
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
