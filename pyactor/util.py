"""
Samples requests::

    msg = TellRequest(TELL,'echo',[],url)
    msg = AskRequest(ASK,'echo',[],future_channel,url)
    msg = AskResponse(result)
    msg = FutureRequest(FUTURE,'get_x',[],'on_result',future_channel,
                            url_to,url_from)

Defined constants:
    FROM, TO, TYPE, METHOD, PARAMS, FUTURE, ASK, TELL, SRC

"""
from gevent import getcurrent
from threading import current_thread
import collections


FROM = 0
TO = 1
TYPE = 2
METHOD = 3
PARAMS = 4
FUTURE = 5
ASK = 6
TELL = 7
SRC = 8

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
        current = getcurrent()
    url = None
    for host in hosts.values():
        if current in host.threads.keys():
            url = host.threads[current]
        elif current in host.pthreads.keys():
            url = host.pthreads[current]
        if url in host.locks.keys():
            # print "At locks",url
            lock = host.locks[url]
            # print lock
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


TellRequest = collections.namedtuple('TellRequest',
                                     'type method params to_url')
# class TellRequest (collections.namedtuple('TellRequest',
#                                           'type method params to_url')):
'''
A namedtuple for the tell requests.
'''
AskRequest = collections.namedtuple('AskRequest',
                                    'type method params channel to_url')
'''
A namedtuple for the ask requests.
'''
AskResponse = collections.namedtuple('AskResponse', 'result')
'''
A namedtuple for the responses of the requests :class:`AskRequest`.
'''
FutureRequest = collections.namedtuple('FutureRequest',
                                       'type method params channel to_url \
                                       future_id')
'''
A namedtuple for the future requests.
'''
FutureResponse = collections.namedtuple('FutureResponse',
                                        'future_id result')
'''
A namedtuple for the future results.
'''

# global AskRequest, TellRquest, AskResponse, FutureRequest
