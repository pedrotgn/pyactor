.. _code:

Main Code
*********

.. automodule:: pyactor

First steps:
============

This library allows the creation and management of actors in a distributed system using Python.
The core of the library is implemented in the three modules explained in this page. That contains
the actors, the proxys that allows them to be accessed from remote locations and the hosts that
put it all together.

First of all, a Host (:class:`context.Host`) is needed in order to create some actors. To create a host, use the
function :func:`context.init_host` which returns the proxy of a host. Then, use this proxy to spawn
actors by giving the class type of the actor to create. The :meth:`context.Host.spawn` method will return the proxy (:class:`proxy.Proxy`)
that manages that actor, but you will need to use the .get() to obtain it from the Future created for the querie when called
the :meth:`context.Host.spawn`which is actualy an ask method of the host actor. See example::

    h = init_host()
    actor1 = h.spawn('id1',MyClass).get()

The class of an actor must have defined its methods in the _tell and _ask lists so they can be called through the proxy.
In the _tell list will be named those methods meant to be asynchronous and in the _ask list, the synchronous ones.
In this example we have a class MyClass with a sync method *ask_me()* and a async method *tell_me()*::

    class MyClass:
        _tell =['tell_me']
        _ask = ['ask_me']
        def tell_me(self,msg):
            print msg
        def ask_me(self):
            return 'hello back'

As you can see, the async method recieves a message and simply prints it while the sync method returns a result.
More basic examples can be found in the 'pyactor/examples' directory of the project: sample1.py, sample2.py and sample3.py.

Actor
=====

.. automodule:: pyactor.actor
    :members:

Proxy
=====

.. automodule:: pyactor.proxy
    :members:

Context
=======

.. automodule:: pyactor.context
    :members:

Util
====

.. automodule:: pyactor.util
    :members:
