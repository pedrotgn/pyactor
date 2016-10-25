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

In ``s1_clientb.py`` we have the same code but the calls are repeated 1000 times.


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

Here we have a registry where Servers can be bind. The registry module starts an
actor which is the registry itself. The first client, binds a server to the
registry and waits for queries. The second one, uses the registry to find the
first one and send work to its server.


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

You can configure your rabbit credentials with:

    setRabbitCredentials('user', 'password')

If you don't, it will use the default Rabbit guest user, which only can connect
locally.
