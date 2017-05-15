.. _remote_tuto:

Remote Tutorial
***************

This page explains the ways of using PyActor for remote communications between
machines.

.. _rs1:

Sample 1 - Basic communication
================================================================================

This example shows the basis on setting a remote communication and sending tell
methods. This is the full code of this sample, which you can find and test in
``pyactor\examples\Remote\s1_server.py``:

.. literalinclude:: ../examples/Remote/s1_server.py
    :linenos:

And ``pyactor\examples\Remote\s1_client.py``:

.. literalinclude:: ../examples/Remote/s1_client.py
    :linenos:

To create a host able to communicate with other machines, simply use as its URL
one with an http scheme, as in the example. Using the http scheme will create
a dispatcher on that host that will manage the queries through xml.

So, the server spawns an actor at ``127.0.0.1:1277`` and the client is able to
look for that actor just giving that IP:port and path. If the client does not
have the Class it is looking for, it must provide the module and the name of
that class when calling the lookup method as shown.

Then, the calls are used as usual.

In ``s1_clientb.py`` we have the same code but the calls are repeated 1000
times.


.. _rs2:

Sample 2 - Basic communication 2
================================================================================

This example extends the first by adding ask queries. This is the full code of
this sample, which you can find and test in
``pyactor\examples\Remote\s2_server.py``:

.. literalinclude:: ../examples/Remote/s2_server.py
    :linenos:

And ``pyactor\examples\Remote\s2_client.py``:

.. literalinclude:: ../examples/Remote/s2_client.py
    :linenos:

This sample is like the previous one, but it includes examples of ask methods.
As the tell methods, they are used as normally, like in the local examples.


.. _rs3:

Sample 3 - Remote spawning
================================================================================

This example shows how to spawn an actor onto another host. This is the full
code of this sample, which you can find and test in
``pyactor\examples\Remote\s3_host.py``:

.. literalinclude:: ../examples/Remote/s3_host.py
    :linenos:

And ``pyactor\examples\Remote\s3_client.py``:

.. literalinclude:: ../examples/Remote/s3_client.py
    :linenos:

In this case the server part only creates its host and makes it serve forever
(:meth:`~serve_forever`). The client is the one that uses :meth:`~.lookup_url`
to get the server reference and spawn an actor in it. Then, sends the work to
the actor. To spawn the actor, as the class of it is defined in the client
module, the method uses a string to do define where is the Class so the server
can import it. This string uses the form ``module/class_name``:

    server = remote_host.spawn('server', 's3_client/Server')

.. note: If the class were defined in both modules, the normal call of
    :meth:`~.spawn` could be used.

.. _rs4:

Sample 4 - Registry example
================================================================================

Here we have a basic example of a registry where some servers can bind to so the
clients are able to see all the servers available and connect to one. This is
the full code of this sample, which you can find and test in
``pyactor\examples\Remote\s4_registry.py``:

.. literalinclude:: ../examples/Remote/s4_registry.py
    :linenos:

And ``pyactor\examples\Remote\s4_client.py``:

.. literalinclude:: ../examples/Remote/s4_client.py
    :linenos:

And ``pyactor\examples\Remote\s4_clientb.py``:

.. literalinclude:: ../examples/Remote/s4_clientb.py
    :linenos:

In this example we have a registry where Servers can be bind. The registry
module starts an actor which is the registry itself to which servers can be
bind and clients look for servers. The first client, binds a server to the
registry and waits for queries to that server. The second one, uses the registry
to find the first one and spawn a server instance on it to afterwards send work
to it.

In order to execute the second client repeatedly without having to restart
all the processes, before spawning the server remotely, it checks if the first
client has already the server by using the method ``has_actor`` on the
remote_host.



.. _sample9:

Sample 9 - Multiple Hosts
================================================================================

This example tests the creation of multiple host at the same time on one unique
execution. This is the full code of this sample, which you can find and test in
``pyactor\examples\Remote\sample9.py``:

.. literalinclude:: ../examples/Remote/sample9.py
    :linenos:

The first thing to make clear is that you should never need to create more than
one host locally, since they are meant for remote communication. This is for
testing purposes.

To create more hosts, you only need to call again the function
:func:`~.create_host`. But you will need to specify different locations for
each host, since those are their identifiers. In the example we create two
hosts in the same location, but attending different ports::

    h = create_host("http://127.0.0.1:6666/host")
    h2 = create_host("http://127.0.0.1:7777/host")

.. note:: Remember that the default address for a host is
    ``local://local:6666/host``

.. note:: To communicate two hosts, both of them must have a remote dispatcher,
    so they must have one of the schemes required.

Now, each host will manage its own actors and threads, so they will need to
communicate through TCP connections.

One thing important to know about this is that only one host can be used to
manage the main execution of your program, so there always will be a main host
and the other ones will be created as secondary hosts.

This main host will be automatically assigned to the first one created. If that
one is closed and there still are other hosts operative, the oldest of them will
assume the role of main host.


.. _rsrbb:

Using RabbitMQ
================================================================================

This library also supports the usage of communication through RabbitMQ queues.
To use this approach, simply define the hosts with an URL with the scheme
`amqp` instead of `http`. This will create a dipatcher for that host that works
with RabbitMQ, and all its actors will work at that scheme.

You can see an example with ``pyactor\examples\Remote\s1_clientrbb.py``:

.. literalinclude:: ../examples/Remote/s1_clientrbb.py
    :linenos:

and ``pyactor\examples\Remote\s1_serverrbb.py``:

.. literalinclude:: ../examples/Remote/s1_serverrbb.py
    :linenos:

You can configure your rabbit credentials with::

    setRabbitCredentials('user', 'password')

If you don't, it will use the default Rabbit guest user, which only can connect
locally.
