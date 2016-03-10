from threading import current_thread


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
