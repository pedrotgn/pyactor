.. _tutorial:

Tutorial
*********

A quick guide on how to use the PyActor library through examples.


.. _install:

Installation
================================================================================

This library allows the creation and management of actors in a distributed system
using Python. It follows the classic actor model and tries to be a simple way to
get two remote actors to quickly communicate.

To install the library use::

    python setup.py install

You can check that works with the examples explained in this page, that you can
find in the ./examples directory of this project. Tested with Python 2.7.

The library requires Gevent, so you may need to install it for using the green
thread version of this library.

It is also available at PYPI, so the most easy way of installing PyActor is by::

    pip install pyactor

Then you can check the examples from `the repository <https://github.com/pedrotgn/pyactor>`_.


.. _global:

Global indications
================================================================================

This library is implemented using two types of concurrence: threads and green
threads (Gevent). To define which one you want, always use the function
:func:`~.set_context` at the beginning of your script. The default value uses
threads but you can specify the mode with one of the following strings:

* ``'thread'``
* ``'green_thread'``

Then, first of all, a :class:`~.context.Host` is needed in order to create some
actors. To create a host, use the function :func:`~.create_host` which returns
a proxy (:class:`~.proxy.Proxy`) to the instance of a :class:`~.Host`.
You should never work with the
instance itself, but always with proxies to maintain the actor model.
When you have the proxy, use it to spawn actors by giving the
class type of the actor to create and one string that will identify it among the
host. The :meth:`~.context.Host.spawn` method will return the proxy
that manages that actor. See example::

    h = create_host()
    actor1 = h.spawn('id1', MyClass)

The class of an actor must have defined its methods in the _tell and _ask lists
so they can be called through the proxy. In the _tell list will be named those
methods meant to be asynchronous and in the _ask list, the synchronous ones.
In this example we have a class MyClass with a sync method *ask_me()* and an
async method *tell_me()*::

    class MyClass:
        _tell =['tell_me']
        _ask = ['ask_me']
        def tell_me(self,msg):
            print msg
        def ask_me(self):
            return 'hello back'

As you can see, the async method receives a message and simply prints it while
the sync method returns a result. More detailed examples can be found in the
'pyactor/examples' directory of the project. They are also explained below as a
tutorial for this library.

.. _sample1:

Sample 1 - Basic
================================================================================

This example shows and tests the most basic elements of this library. It creates
a :class:`~.Host` and adds an actor to it. Then, queries an async method of this
actor. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample1.py``:

.. literalinclude:: ../examples/sample1.py
    :linenos:

The example is similar to the one shown above in :ref:`global`, but here we'll
explain it more carefully.

In this case, we need to import the :func:`~.create_host` function from the
project in order to use it. We also import the *sleep* function, to give time to
the actor to work, and the setting function for the type, :func:`~.set_context`.
Finally, we also need the :func:`~.shutdown` function to stop and clean the host
before finishing.

The actor to create in this example will be an :class:`Echo`. This class only
has one method which prints the message *msg*, given by parameter. As you can
see, the classes destined to be actors must have the attributes ``_tell=[]``
and ``_ask=[]`` that include the names of the methods that can be remotely
invoked in an asynchronous or synchronous way, respectively. In this sample we
have the echo method, which is async, as no response from it is needed.

.. note:: In this sample we have the _ask list also defined as a learning purpose,
    but you could just not write that list if none method goes there.

The first thing to do is define which model are we going to use. For the moment
we are using the classic threads, so we'll call the function without parameters
to use the default solution. ::

    set_context()

To begin the execution we'll need a :class:`~.Host` to contain the actors. For
that, we create a new variable by using the function we imported before. ::

    h = create_host()

Now we have a :class:`~.Host` in the 'h' variable. Actually, as Host objects are
also actors, this call returns  a :class:`Proxy` that will manage that actor.
It can create actors attached
to itself. To do that, we use the :meth:`~.Host.spawn` method. The first
parameter is a string with the ID of the actor that will identify it among the
host so no repeated values are allowed. The second is the class the actor will
be instance of. In this case we create an actor which will be an :class:`Echo`
and with the id 'echo1'::

    e1 = h.spawn('echo1',Echo)

'e1' will now represent that actor (actually, the :class:`Proxy` that manages
it).

As we have the actor, we can invoke his methods as we would do normally since
the proxy will redirect the queries to the actual placement of it. If we didn't
have specified the methods in the statements appointed before (_tell and _ask),
we wouldn't be able to do this now, giving a 'no such attribute error'.
The execution should work properly and print on screen::

    hello there !!

Then, the sleep gives time to the actor for doing the work and finally, we close
the host, which will stop all its actors. This function (:func:`~.shutdown`)
should be always called at the end::

    shutdown()

.. note:: As the host is an actor itself, it has sync and async methods and can
    receive remote queries if we use its proxy.

..note:: As said, he host is also a living actor so it could receive queries remotely in the
    future. This means you can send its reference to another host, which allows to
    spawn remotely (remote spawns require a bit more info, see the remote
    tutorial).

.. note:: Now you can try and see how it works with green threads by just
    specifying 'green_thread' in the setting function.
    ``set_context('green_thread')``


.. _sample2:

Sample 2 - Sync
================================================================================

This example extends the content of the previous one by including sync queries.
It still creates a :class:`~.Host` and adds an actor to it. This is the full
code of this sample, which you can find and test in
``pyactor\examples\sample2.py``:

.. literalinclude:: ../examples/sample2.py
    :linenos:

Now :class:`Echo` has two new methods, :meth:`bye` and :meth:`say_something`.
The first one is async like the previous :meth:`echo`, but the other one is
synchronous.

The invocation of ask methods is simply the same you would do normally.

The correct output for this sample is the following::

    hello there !!
    bye
    something


.. _sample3:

Sample 3 - Callback
================================================================================

This example tries the functionality of the callback element of the synchronous
queries. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample3.py``:

.. literalinclude:: ../examples/sample3.py
    :linenos:

This time we keep having the same initialization as before, but now there is
a new class. :class:`Bot` has three async methods that will allow to prove the
callback functionality. :meth:`set_echo` registers an
:class:`Echo` to the Bot so it can call it. :math:`ping` creates the query for
the :meth:`say_something` method and sets the callback for this to his other
method :meth:`pong`. This second will receive the result of the execution of the
:meth:`say_something` method.

In order to add a callback, the sync call must be defined as a Future. We do
this by adding the parameter `future=True` to the call. This will make the query
return a :class:`~.Future` instance instead of the result. That means that the
execution of the query may has not been completed yet. To get the result from a
Future, use the method :meth:`~.result` as you can see inside the `pong` method.

To add a callback use the Future method :meth:`~.add_callback` which takes by
parameter the name of the method to callback, which is one from the actor that
calls it. You can add various callbacks to one future, and them will be called
in order when the work is finished. Also, if you add a callback to a finished
future, it will be directly invoked.

It is also possible to add a callback to a method from another actor by passing
also its proxy. See :ref:`sample11` for more deep detail in Futures.

.. note:: :meth:`~.add_callback` needs to be called from an actor to another
    actor, specifying a method of an actor (also the actor, if it is different
    from the one that makes the addition).

.. note:: The method treated as a callback must have one unique parameter, which
    is the future. Inside the method you can use :meth:`~.result` to get the
    result of the call (exceptions can be raised) or :meth:`~.exception` to get
    the instance of a possible raised exception. You can also check the state of
    the future with one of its methods: :meth:`~.done` or :meth:`~.running`.

The correct output for this sample is the following::

    pinging...
    callback something



.. _sample4:

Sample 4 - Timeout
================================================================================

This example tests the raising of timeouts. This is the full code of this
sample, which you can find and test in ``pyactor\examples\sample4.py``:

.. literalinclude:: ../examples/sample4.py
    :linenos:



Now we have the same :class:`Echo` class but in the sync method we added a sleep
of 2 seconds. Also, we surrounded the call of the method by a try structure
catching a :class:`~.TimeoutError` exception. Since we are giving to the invocation
a expire time of 1 second, the timeout will be reached and the exception raised.


You can set a timeout for the query if you like. For that, add the parameter with
the tag `timeout=X` in the call, in seconds. ::

    x = e1.say_something(timeout=3)

The default timeout is 1 second. To wait indefinitely, just set it to `None`.

The correct output for this sample is the following::

    hello there !!
    bye
    timeout caught


.. _sample5:

Sample 5 - Lookup
================================================================================

This example shows the usage of the lookup methods applied to a host. This is
the full code of this sample, which you can find and test in
``pyactor\examples\sample5.py``:

.. literalinclude:: ../examples/sample5.py
    :linenos:

We have two ways to get the reference of one already existing actor of a host.
If it is local, of the same host, it is fine to use the method :meth:`~.lookup`
giving by parameter only the id of the actor you wish::

    e = h.lookup('echo1')

If you are working remotely, you could need :meth:`~.lookup_url` to get the
reference. In this example, it is used also to get a local reference giving the
standard local url at which the host is initialized by default::

    ee = h.lookup_url('local://local:6666/echo1')


.. _sample6:

Sample 6 - self.id, proxy and host
================================================================================

This example tests the self references to actors id and proxy. This is the full
code of this sample, which you can find and test in
``pyactor\examples\sample6.py``:

.. literalinclude:: ../examples/sample6.py
    :linenos:

This sample demonstrates how to get references to an actor from the actor
itself. With ``self.id`` we obtain the string that identifies the actor in the
host it is located, ``self.url`` contains its network location. Then, with
``self.proxy`` you can get a reference to a proxy
managing the actor so you can give it to another function, class or module in a
safe and easy way.

It is also possible to use ``self.host``, which will give a proxy to the host in
which the actor is so you can :meth:`~.lookup` other actors from there.

In the example, we use these three calls to send various salutations from a
:class:`Bot` to an :class:`Echo` giving by parameter also a proxy from the Bot
so the Echo can call one of Bot's methods in order to get its id. Also, the
:meth:`set_echo` method, in this case, does not receive the Echo by parameter.
It uses the inside reference it already has to call a :meth:`~.lookup` to the
host and get the wanted reference.

Also notice that every proxy has the methods ``get_id`` and ``get_url`` already
defined, so you can get the actor's information directly from the proxy.

The correct output for this sample is the following::

    hello from: bot1
    hi from: bot1
    hey from: bot1
    what`s up? from: bot1
    Press Ctrl+C to kill the execution

In this sample, we also see the usage of the :func:`~.serve_forever` function
which is very useful in remote communication in order to keep a host alive as
another one sends queries to his actors. The usage is very simple, instead of
shutting the host down at the end, we call::

    serve_forever()

This will maintain the host alive in lower process consumption until the user
presses ``Ctrl+C`` allowing other hosts to lookup and call methods from actors
in this host.

.. _sample7:

Sample 7 - references
================================================================================

This example tests the sending of proxy references by parameter using the
definition of the _ref list. This is the full code of this sample, which you can
find and test in ``pyactor\examples\sample7.py``:

.. literalinclude:: ../examples/sample7.py
    :linenos:

The previous examples may pass proxy references by parameter in its methods, but
they are sharing the same instance of a proxy. This could cause various problems
of concurrency so we might want different proxies in different spots. To achieve
that, you have to indicate that a method receives or returns a proxy by adding
it to the _ref list of the class (it yet must be in _ask or _tell).

With this indication, pyActor will search for proxies in the parameters and make
a new proxy for the actor in the context that the method will be executed (the
actor's).

Bot has a method ``set_echo`` that gets the echo it will use by parameter. As
this echo has to be a proxy, Bot includes the next definition::

    _ref = ['set_echo']

So then, at the main code, we can make this call without any future concurrency
problems, as the proxies are not shared::

    bot.set_echo(e1)

Also seen in the example, Echo has methods that receive a proxy, in this methods
you can see examples of passing proxies even inside lists or dictionaries.

Although the proxies are different, you may yet compare them directly so when
using ``p1 == p2`` on two proxies, the comparison will be done on the actors
that they represent and not on the proxy instance itself.
See the basic examples on ``proxies_test.py``.


.. _sample8:

Sample 8 - Parallel
================================================================================

This example tests the creation and execution of actors with parallel methods.
This is the full code of this sample, which you can find and test in
``pyactor\examples\sample8.py``:

.. literalinclude:: ../examples/sample8.py
    :linenos:

Parallels are a way of letting one actor to process many queries at a time.
This will allow the actor to keep receiving calls when another call has been
blocked with another job (an I/O call or a synchronous call to another actor).

To make one method execute parallel, you need to specify it in the class attribute
_parallel, which is a list. The method must also be in one of the lists _tell or
_ask. The methods with this tag will be executed in new threads so their execution
do not interfere with other queries. That is, the actor can attend other queries
while executing the parallel method.

As you could think, executing methods of the same actor at the same time can compromise
the integrity of data. PyActor ensures that only one thread is executing on an
actor at the same time, allowing other threads to execute when the one executing
is blocked with some call. This prevents two threads from accessing the same data
at a time, but is up to the programmer to prevent the data to change during the
execution of a method if that is not intended, as a method could modify a property
of the actor while a parallel, that operates with that data, is blocked, leading
to an inconsistency.

In this example we have three classes: File, Web and Workload. File represents a
server that serve the download of files. Simulates the work with a sleep.
Web represents a web server which contains a list of files. It has to have a file
server that provide the files and can list its files (list_files) and return one
of them (get_file). Workload is the class that will do the work. It asks the web
to list its files ten times, or request to download one of the files.

The execution is simple, we create one file server, one web server and attach the
file server to the web::

    web.remote_server(f1)

Then lets do the work. Create two Workload instance and pass to them the web server
we created::

    load = host.spawn('wl1', Workload)
    load.remote_server(web)
    load2 = host.spawn('wl2', Workload)
    load2.remote_server(web)

The first worker will make the ten queries to list_files, while the second one
will download a file::

    load.launch()
    load2.download()

As the method get_file is marked as parallel, its execution will be done in another
thread, so when the method blocks downloading (in the sleep), it will free the actor
so it can keep serving answers to the first load.

If we do not use parallels in this example (which you can try by commenting the
right line as indicated) some of the calls to the list_files method will raise
TimeoutError as the thread of that actor is blocked with the download.

.. note:: `sample8b` combines this example with the use of Futures.

.. note:: You can test another parallel example with `parall.py`.


.. _sample_inter:

Sample 10 - Intervals
================================================================================

This example tests the usage of intervals that allow an actor to periodically do
an action. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample10.py``:

.. literalinclude:: ../examples/sample10.py
    :linenos:

To generate intervals, we use the functions :func:`context.interval` and
:func:`context.later` that can be imported if needed. The
class (actor) will call the first one giving firstly the proxy of the host that
will manage the interval, accessible from within the actor by `self.host`; next,
the interval time and the proxy to the actor to which make the periodic call
(that can be itself with `self.proxy` or another actor) as
well as the name of the method in that actor that will be called.
The method to be executed must be a tell method (with ref or without it), otherwise,
it will raise and exception.

This function returns an interval instance
that we have to keep in order to stop it later by calling *.set()*.

In this example we use :func:`context.later` to set a timer that will stop the
interval after a certain time. This method works similar to the other. You
specify by parameter the actor and the method to be executed after that time,
and only accepts methods of the tell type.

If the method requires arguments, those have to be after the three base. In the
example, hello needs one argument and it is passed as::

    self.host.interval(1, self.proxy, "hello", "you")

If the method needed two of them, it will be like follows::

    self.host.interval(1, self.proxy, "hello", "you", "too")


.. _sample11:

Sample 11 - Futures
================================================================================

This example tests more deeply the functionalities of futures. This is the full
code of this sample, which you can find and test in
``pyactor\examples\sample10.py``:

.. literalinclude:: ../examples/sample11.py
    :linenos:

Not much to explain here, just see it by yourself. The example is like Sample 3,
but here we set various callbacks and some to another actor.

Also shows the usage of the consulting methods of futures: :meth:`~.done`,
:meth:`~.result`, :meth:`~.exception`.

Change between this lines::

    ask = e1.raise_something(future=True)
    ask = e1.say_something(future=True)

to check the raising of exceptions.

Finally, note that the only argument for :meth:`~.result` (also for
:meth:`~.exception`) is the timeout: the time, in seconds, to wait for a result.


.. _sample1b:

Sample 1b - Stopping an Actor (Advanced)
================================================================================

This example is like the first one, but extended with a new functionality for
the hosts. This shows how to stop an actor and delete all its references from
one host. This is the full code of this sample, which you can find and test in
``pyactor\examples\sample1b.py``:

.. literalinclude:: ../examples/sample1b.py
    :linenos:

You can always delete an actor by calling the method :meth:`~.stop_actor` of its
host. This function will stop the thread of that actor and all its references
from the host. This means the actor cannot be looked up anymore, it will not
receive any more work and you can create a future actor with its same id.

.. note:: Parallel queries already submitted will end as usual.

.. note:: Intervals involving that actor's methods might result in errors.
