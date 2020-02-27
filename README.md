# **PyActor**

-----------------------------

## _The minimalistic python actor middleware_

-----------------------------

[![PyPI version](https://badge.fury.io/py/pyactor.svg)](https://badge.fury.io/py/pyactor)

PyActor is a python actor middleware for an object oriented architecture
constructed with the idea of getting two remote actors
to quickly communicate in a very simple, lightweight and minimalistic way.

It supports two versions:

* Threading
* Gevent green threads

<!-- +graphic tests -->

It also includes communication between machines using XMLRPC and a second version
that uses RabbitMQ message system in a transparent way.

### Installation

Install using:

    python setup.py install

Check that works executing the examples:

    cd examples
    python sample1.py
    ...

Check also the docs for a tutorial:

[![Documentation Status](https://readthedocs.org/projects/pyactor/badge/?version=master)](http://pyactor.readthedocs.io/en/master/?badge=master)

Commits are build and tested automatically at [Travis-CI](https://travis-ci.org/pedrotgn/pyactor).

[![Build Status](https://travis-ci.org/pedrotgn/pyactor.svg?branch=master)](https://travis-ci.org/pedrotgn/pyactor)

See code coverage at [codecov.io](https://codecov.io/gh/pedrotgn/pyactor) or [coveralls.io](https://coveralls.io/github/pedrotgn/pyactor)

[![Coverage Status](https://codecov.io/gh/pedrotgn/pyactor/branch/master/graph/badge.svg)](https://codecov.io/gh/pedrotgn/pyactor)
<!-- [![Coverage Status](https://coveralls.io/repos/github/pedrotgn/pyactor/badge.svg?branch=master)](https://coveralls.io/github/pedrotgn/pyactor?branch=master) -->

<!-- %%%% Landscape kind of died. %%%%%%
The code is also checked for its health at every push by [landscape.io](https://landscape.io/github/pedrotgn/pyactor)
(PEP8, common bad smells, etc.):

[![Code Health](https://landscape.io/github/pedrotgn/pyactor/master/landscape.svg?style=flat)](https://landscape.io/github/pedrotgn/pyactor/master)
 -->
 
## First steps

This library is implemented using two types of concurrence:

* ``'thread'`` : classic threads
* ``'green_thread'`` : Gevent

Green threads give a performance almost twice better.

You will need to specify which one you are going to use at the beginning of your
script with ``set_context('TYPE')``. Where type is one of the two keywords
above.

Then, first of all, a `Host` is needed in order to create some actors.
Use it to spawn actors by giving the class type of the actor to create
and one string that will identify it among the host. See example:

    h = create_host()
    actor1 = h.spawn('id1', MyClass)

The class of an actor must have defined its methods in the _tell and _ask sets
so they can be called through the proxy. In the _tell set will be named those
methods meant to be asynchronous and in the _ask set, the synchronous ones.
In this example we have a class ``MyClass`` with a sync method *ask_me()* and an
async method *tell_me()*:

    class MyClass:
        _tell = {'tell_me'}
        _ask = {'ask_me'}
        def tell_me(self, msg):
            print msg
        def ask_me(self):
            return "hello back"

As you can see, the async method receives a message and simply prints it while
the sync method returns a result. You can now call this methods from your main
code:

    actor1.tell_me("Hello")
    print actor1.ask_me()

## Remote connections

Unlike other library solutions, PyActor supports remote communication between
various machines by only giving an IP to the host. For example:

    host = create_host('http://127.0.0.1:1277/')

And this host is online, so the other machine only needs to lookup for it:

    host = create_host('http://127.0.0.1:1679')
    remote_host = host.lookup_url('http://127.0.0.1:1277/', Host)

Or directly get one of its actors:

    c = host.lookup_url('http://127.0.0.1:1277/id1', 'MyClass', 'module')

## Tutorial

PyActor has many examples and a tutorial explaining all its features.
This examples can be found in the
'pyactor/examples' directory of the project. They are also explained in the
documentation as a tutorial, hosted at [readthedocs.org](http://pyactor.readthedocs.io/en/master/?badge=master).
