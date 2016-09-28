"""
Defined constants:
    FROM, TO, TYPE, METHOD, PARAMS, FUTURE, ASK, TELL, SRC,
    CHANNEL, CALLBACK, ASKRESPONSE, FUTURERESPONSE, RESULT, RPC_ID

"""
from gevent import getcurrent
from threading import current_thread
import collections


FROM = 'FROM'
TO = 'TO'
TYPE = 'TYPE'
METHOD = 'METHOD'
PARAMS = 'PARAMS'
FUTURE = 'FUTURE'
ASK = 'ASK'
TELL = 'TELL'
SRC = 'SRC'
CHANNEL = 'CHANNEL'
CALLBACK = 'CALLBACK'
ASKRESPONSE = 'ASKR'
FUTURERESPONSE = 'FUTURER'
RESULT = 'RESULT'
RPC_ID = 'RPC_ID'

main_host = None
core_type = None
hosts = {}


def get_host():
    if core_type == 'thread':
        current = current_thread()
    else:
        current = getcurrent()
    for host in hosts.values():
        if current in host.threads.keys():
            return host
        elif current in host.pthreads.keys():
            return host
    return main_host


def get_current():
    if core_type == 'thread':
        current = current_thread()
    else:
        current = getcurrent()
    for host in hosts.values():
        if current in host.threads.keys():
            return host.actors[host.threads[current]]
        elif current in host.pthreads.keys():
            return host.actors[host.pthreads[current]]


def get_lock():
    if core_type == 'thread':
        current = current_thread()
    else:
        return None
    url = None
    for host in hosts.values():
        if current in host.threads.keys():
            url = host.threads[current]
        elif current in host.pthreads.keys():
            url = host.pthreads[current]
        if url in host.locks.keys():
            lock = host.locks[url]
            return lock


class TimeoutError(Exception):
    def __init__(self, meth='Not specified'):
        self.method = meth

    def __str__(self):
        return ("Timeout triggered: %r" % self.method)


class AlreadyExistsError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Repeated ID: %r" % self.value)


class NotFoundError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Not found ID: %r" % self.value)


class HostDownError(Exception):
    def __str__(self):
        return ("The host is down.")


class HostError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Host ERROR: %r" % self.value)


class FutureError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Future ERROR: %r" % self.value)


def ref_l(f):
    def wrap_ref_l(*args):
        new_args = list(args)
        new_args[0][PARAMS] = get_host().loads(list(args[0][PARAMS]))
        return f(*new_args)
    return wrap_ref_l


def ref_d(f):
    def wrap_ref_d(*args):
        new_args = list(args)
        new_args[0] = get_host().dumps(args[0])
        return f(*new_args)
    return wrap_ref_d
