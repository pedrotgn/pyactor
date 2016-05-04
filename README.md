# PyActor README
-----------------------------

[![Build Status](https://travis-ci.org/pedrotgn/pyactor.svg?branch=master)](https://travis-ci.org/pedrotgn/pyactor)
[![codecov](https://codecov.io/gh/pedrotgn/pyactor/branch/master/graph/badge.svg)](https://codecov.io/gh/pedrotgn/pyactor)
PyActor is a python actor library constructed with the idea of getting two remote objects
to quickly communicate in a very simple and minimalistic way.

Currently in a very primitive phase.

Install using:
python setup.py install

Check that works executing the examples:
cd examples
python sample1.py
...

Also see the documentation in doc/_build/html/index.html



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
