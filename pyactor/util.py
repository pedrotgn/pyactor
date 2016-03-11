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

global actors
global threads
actors = {}
threads = {}

def get_current():
    current = current_thread()
    if threads.has_key(current):
        return threads[current]

class Timeout(Exception):pass

TellRequest = collections.namedtuple('TellRequest', 'type method params to_url')
AskRequest = collections.namedtuple('AskRequest', 'type method params channel to_url')
AskResponse = collections.namedtuple('AskResponse', 'result')
FutureRequest = collections.namedtuple('FutureRequest', 'type method params callback channel to_url from_url')

#global AskRequest, TellRquest, AskResponse, FutureRequest

"""
Samples requests:
msg = TellRequest(TELL,'echo',[],url)
msg = AskRequest(ASK,'echo',[],future_channel,url)
msg = AskResponse(result)
msg = FutureRequest(FUTURE,'get_x',[],'on_result',future_channel,url_to,url_from)

"""
