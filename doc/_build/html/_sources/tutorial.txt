.. _tutorial:

Tutorial
*********

A quik guide on how to use the PyActor library through examples.


.. _install:

Installation
================================================================================

This library allows the creation and management of actors in a distributed system using Python. It follows the
classic actor model and tries to be a simple way to get two remote objects to quickly commnicate.

To install the library use::

    python setup.py install

You can check that works with the examples explained in this page.


.. _global:

Global indications
================================================================================

First of all, a :class:`~.context.Host` is needed in order to create some actors. To create a host, use the
function :func:`~.create_host` which returns the instance of a :class:`~.Host`. Then, use it to spawn
actors by giving the class type of the actor to create and one string that will identify it among the host.
The :meth:`~.context.Host.spawn` method will return the proxy (:class:`~.proxy.Proxy`)
that manages that actor. See example::

    h = create_host()
    actor1 = h.spawn('id1',MyClass)

The class of an actor must have defined its methods in the _tell and _ask lists so they can be called through the proxy.
In the _tell list will be named those methods meant to be asynchronous and in the _ask list, the synchronous ones.
In this example we have a class MyClass with a sync method *ask_me()* and an async method *tell_me()*::

    class MyClass:
        _tell =['tell_me']
        _ask = ['ask_me']
        def tell_me(self,msg):
            print msg
        def ask_me(self):
            return 'hello back'

As you can see, the async method recieves a message and simply prints it while the sync method returns a result.
More detailed examples can be found in the 'pyactor/examples' directory of the project.
They are also explained below as a tutorial for this library.

.. _sample1:

Sample 1 - Basic
================================================================================

This example shows and tests the most basic elements of this library. It creates a :class:`~.Host` and adds an actor to it.
Then, queries an async method of this actor. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample1.py``:

.. literalinclude:: ..\examples\sample1.py
    :linenos:

This example is similar to the one shown above in :ref:`global`, but here we'll explain it more carefully.

In this case, we need to import the :func:`~.create_host` function from the project in order to use it.
We also import the *sleep* function to give time to the actor to work.

The actor to create in this example will be an :class:`Echo`. This class only has one method which prints
the message *msg*, given by parameter. As you can see, the classes destinated to be actors must have the
atributes ``_tell=[]`` and ``_ask=[]`` that include the names of the methods that can be
remotely invoked in an asynchronous or synchronous way, respectively. In this sample we have the echo method,
which is async, as no response from it is needed.

To begin the execution we'll need a :class:`~.Host` to contain the actors. For that, we create a new variable
by using the function we imported before. ::

    h = create_host()

Now we have a :class:`~.Host` in the 'h' variable. It can create actors atached to itself. To do that, we use
the :meth:`~.Host.spawn` method. The first parameter is a string with the id of the actor that will identify it
among the host so no repeated values are allowed. The second is the class the actor will be instance of. In this case
we create an actor which will be an :class:`Echo` and with the id 'echo1'::

    e1 = h.spawn('echo1',Echo)

'e1' will now represent that actor (the :class:`Proxy` that manages it).

As we have the actor, we can invoke his methods as we would do normally since the proxy will redirect the queries
to the actual ubication of it. If we didn't have specified the methods in the statements appointed before (_tell and _ask),
we would't be able to do this now.
The execution shold work properly and print on screen::

    hello there !!

The host is also a living actor so it could recieve queries remotely in the future. To get its proxy, we use::

    hr = h.proxy

And now we have a proxy managing the host in *hr* that we could use to send references remotely. This allows to
spawn remotely, although in this example we are doing it all locally:

    e2 = hr.spawn('echo2',Echo).get()

The use of *.get()* at the end is necessary since 'hr' is a :class:`Proxy` of the host
and :meth:`~.spawn` is treated like an async method which result has to be obtained.


Then, the sleep gives time to the actor for doing the work and finally, we close the host, which will stop all
its actors. This function (:meth:`~.shutdown`) should be allways called at the end::

    h.shutdown()

.. note:: As the host is an actor itself, it has sync and async methods and can recieve remote queries if we use its proxy.

.. _sample2:

Sample 2 - Sync
================================================================================

This example extends the content of the previous one by including sync queries. It still creates a :class:`~.Host`
and adds an actor to it. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample2.py``:

.. literalinclude:: ..\examples\sample2.py
    :linenos:

Now :class:`Echo` has two new methods, :meth:`bye` and :meth:`say_something`. The first one is async like
the previous :meth:`echo`, but the other one is synchronous.

In this example we see that, when invoking a synchronous method is needed to add the *.get()* in order to actually
execute the method and obtain a result from it. If you forget to use it, the function will return a :class:`~.Future`
which is the formulation of the query, but it has not been invoked yet.

The correct output for this sample is the following::

    hello there !!
    bye
    something


.. _sample3:

Sample 3 - Callback
================================================================================

This example tries the functionality of the callback element of the synchronous queries. This is the full code of this
sample, which you can find and test in ``pyactor\examples\sample3.py``:

.. literalinclude:: ..\examples\sample3.py
    :linenos:

This time we keep having the same initialitzation as before, but now threre is a new class. :class:`Bot` has three async
methods that will allow to prove the correctness of the callback functionality. :meth:`set_echo` registers an :class:`Echo`
to the Bot so it can call it. :math:`ping` creates the query for the :meth:`say_something` method and sets the callback for this
to his other method :meth:`pong`. This second will recieve the result of the execution of the :meth:`say_something` method.

.. note:: :meth:`~.add_callback` needs to be called from an actor to another actor, specifing a method of the first one that has
    one parameter, which will be the result of the method invoked.

The correct output for this sample is the following::

    pinging...
    callback something



.. _sample4:

Sample 4 - Timeout
================================================================================

This example tests the raising of timeouts. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample4.py``:

.. literalinclude:: ..\examples\sample4.py
    :linenos:

Now we have the same :class:`Echo` class but in the sync method we added a sleep of 2 seconds. Also, we sorrounded
the call of the method by a try structure catching a :class:`~.Timeout` exception. Since we are giving to the invocation
a expire time of 1 second, the timeout will be reached and the exception rised.

.. note:: The parameter of the .get() method is the time, in seconds, that is given as a timeout to the query. The
    default one, in case none is specified, is 1 second.

The correct output for this sample is the following::

    hello there !!
    bye
    timeout catched


.. _sample5:

Sample 5 - Lookup
================================================================================

This example shows the usage of the lookup methods applied to a host. This is the full code of this sample, which
you can find and test in ``pyactor\examples\sample5.py``:

.. literalinclude:: ..\examples\sample5.py
    :linenos:

We have two ways to get the reference of one already existing actor of a host. If it is local, of the same host,
it is fine to use the method :meth:`~.lookup` giving by parameter only the id of the actor you wish::

    e = h.lookup('echo1')

If you are working remotly, you could need :meth:`~.lookup_url` to get the reference. In this example, it is used
also to get a local reference giving the standard local url at which the host is initialized by default::

    ee = h.lookup_url('local://local:6666/echo1')

.. note:: Remember that if you are using the proxy for the host, you need to use *.get()*.



.. _sample6:

Sample 6 - self.id, proxy and host
================================================================================

This example tests the self references to actors id and proxy. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample6.py``:

.. literalinclude:: ..\examples\sample6.py
    :linenos:

This sample demonstrates how to get references to an actor from the actor itself. With ``self.id`` we obtain the string
that identifies the actor in the host it is located.
Then, with ``self.proxy`` you can get a reference to a proxy managing the actor so you can give it to
another function, class or module in a safe and easy way.

It is also possible to use ``self.host``, which will give a proxy to the host in which the actor is
so you can :meth:`~.lookup` other actors from there.

In the example, we use these three calls to send various salutations from a :class:`Bot` to an :class:`Echo`
giving by parameter also a proxy from the Bot so the Echo can call one of Bot's methods in order to get its id.
Also, the :meth:`set_echo` method, in this case, do not recieve the Echo by parameter. It uses the inside reference
it already has to call a :meth:`~.lookup` to the host and get the wanted reference.

The correct output for this sample is the following::

    hello from: bot1
    hi from: bot1
    hey from: bot1
    what`s up? from: bot1
    Press Ctrl+C to kill the execution

In this sample, we also see the usage of the :func:`~.serve_forever` function wich is very useful in remote communication
in order to keep a host alive as another one send queries to his actors. The usage is very simple, instead of shuting
the host down at the end, we call::

    serve_forever()

This will maintain the host alive in lower process consumption until the user presses ``Ctrl+C`` allowing other hosts
to lookup and call methods from actors in this host.


Sample 7 - references
================================================================================

This example tests sending of proxy references by parameter using the ref decorator. This is the full code of this sample,
 which you can find and test in ``pyactor\examples\sample7.py``:

.. literalinclude:: ..\examples\sample6.py
    :linenos:

The previous examples pass proxy references by parameter in its methods, but them are sharing the same instance of a proxy.
This could cause various problems of concurrency so we might want diferent proxies in different spots. To achive that, you
have to indicate that a method recieves or returns a proxy with ``@ref`` which is imported from ``pyactor.proxy``.


.. _sample_inter:

Intervals
===========

This example tests the usage of intervals that allow an actor to periadically do an action. This is the full code of this sample,
 which you can find and test in ``pyactor\examples\intervals.py``:

.. literalinclude:: ..\examples\intervals.py
    :linenos:

To generate intervals, we need to import :func:`~.interval_host` and :func:`~.later` from intervals module.
The class will call the first one giving the interval time and the function to execute, along with the host proxy
that can be obtained with ``self.proxy``. This function returns an interval instance that we have to keep in order
to stop it after by calling *.set()*.
In this example we use :func:`~.later` to set a timer that will stop the interval after a certain time.


Parallel
==========
