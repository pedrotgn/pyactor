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
look for that actor just giving that IP:port and path.

Then, the calls are used as usual.

In ``s1_clientb.py`` we have the same code but the calls are repeated 1000 times.
