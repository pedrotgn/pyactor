# Pyactor README
-----------------------------

Install using:
python setup.py install

Check that works executing the examples:

cd examples
python sample1.py


## Messages
---------------


TELL: PROXY -> ACTOR
(_from, self.__target, TELL, self.__method,args)


ASK: ACTOR -> FUTURE
result

FUTURE: ACTOR -> CLIENT
(msg[TO],msg[FROM],TELL, msg[FUTURE],[result])


FROM = 0
TO = 1
TYPE = 2
METHOD = 3
PARAMS = 4
FUTURE = 5
ASK = 6
TELL = 7
SRC = 8
