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
hosts = {}


def get_host():
    current = current_thread()
    for host in hosts.values():
        if current in host.threads.keys():
            return host
        elif current in host.pthreads.keys():
            return host
    return main_host


def get_current():
    current = current_thread()
    for host in hosts.values():
        if current in host.threads.keys():
            return host.actors[host.threads[current]]
        elif current in host.pthreads.keys():
            return host.actors[host.pthreads[current]]


def get_lock():
    current = current_thread()
    for host in hosts.values():
        url = None
        if current in host.threads.keys():
            url = host.threads[current]
        elif current in host.pthreads.keys():
            url = host.pthreads[current]
        if url in host.locks.keys():
            # print "At locks",url
            lock = host.locks[url]
            # print lock
            return lock


class Timeout(Exception):
    pass


class AlreadyExists(Exception):
    pass


class NotFound(Exception):
    pass


class HostDown(Exception):
    pass


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
                                       'type method params callback channel \
                                        to_url from_url')
'''
A namedtuple for the future requests.
'''

# global AskRequest, TellRquest, AskResponse, FutureRequest
