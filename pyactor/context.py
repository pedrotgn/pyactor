from signal import SIGINT
import types
import sys
import os.path

from urlparse import urlparse
from proxy import Proxy, set_actor, ProxyRef, TellWrapper
from exceptions import HostDownError, AlreadyExistsError, NotFoundError,\
    HostError, IntervalError
import util

core_type = None
available_types = ['thread', 'green_thread']


def setRabbitCredentials(user, passw):
    '''
    If you use a RabbitMQ server an want to make remote queries, you might
    need to specify new credentials for connection.

    By default, PyActor uses the guest RabbitMQ user.

    :param str. user: Name for the RabbitMQ user.
    :param str. passw: Password for the RabbitMQ user.
    '''
    util.RABBITU = user
    util.RABBITP = passw


def set_context(module_name='thread'):
    '''
    This function initializes the context of execution deciding which
    type of threads are being used: classic python threads or green
    threads, provided by Gevent.

    This should be called first of all in every execution, otherwise,
    the library would not work.

    The default module is 'thread'.

    :param str. module_name: Name of the module you want to use
        ('thread' or 'green_thread').
    '''
    global core_type
    if core_type is None and module_name in available_types:
        core_type = module_name
        util.core_type = core_type
        global actor
        actor = __import__('pyactor.' + module_name + '.actor', globals(),
                           locals(), ['Actor', 'ActorRef'], -1)
        global intervals
        intervals = __import__('pyactor.' + module_name + '.intervals',
                               globals(), locals(),
                               ['interval_host', 'sleep', 'later'], -1)
        global parallels
        parallels = __import__('pyactor.' + module_name + '.parallels',
                               globals(), locals(),
                               ['ActorParallel'], -1)
        global future
        future = __import__('pyactor.' + module_name + '.future',
                            globals(), locals(), ['FutureManager'], -1)
        set_actor(module_name)
        global rpcactor
        rpcactor = __import__('pyactor.' + module_name + '.rpcactor',
                              globals(), locals(), ['RPCDispatcher'], -1)
        global signal
        if module_name == 'green_thread':
            signal = __import__('gevent', ['signal'])
        else:
            signal = __import__('signal', ['signal'])
    else:
        raise Exception('Bad core type.')


def create_host(url="local://local:6666/host"):
    '''
    This is the main function to create a new Host to which you can
    spawn actors. It will be set by default at local address if no
    parameter *url* is given, which would result in remote
    incomunication between hosts. This function shuould be called once
    for execution or after callig :meth:`~.shutdown` to the previous
    host.

    Nevertheless, it is possible to create locally more than one host
    and simulate a remote communication between them if they are of some
    remote type (`http` or `amqp`), but the first one created will
    be the main host, which is the one that will host the queries from
    the main function.
    Of course, every host must be initialized with a diferent URL(port).
    Although that, more than one host should not be requiered for any real
    project.

    :param str. url: URL where to start and bind the host.
    :return: :class:`~.Proxy` to the new host created.
    :raises: Exception if there is a host already created with that URL.
    '''
    if url in util.hosts.keys():
        raise HostError('Host already created. Only one host can' +
                        ' be ran with the same url.')
    else:
        if not util.hosts:
            util.main_host = Host(url)
            util.hosts[url] = util.main_host
        else:
            util.hosts[url] = Host(url)
        return util.hosts[url].proxy


class Host(object):
    '''
    Host must be created using the function :func:`~create_host`.
    Do not create a Host directly.

    Host is the container of the actors. It manages the spawn and
    elimination of actors and their communication through channels. Also
    configures the remote points where the actors will be able to receive
    and send queries remotely. Additionaly, controls the correct management of
    the threads and intervals of its actors.

    The host is managed as an actor itself so you interact with it through
    its :class:`~.Proxy`. This allows you to pass it to another host to
    spawn remotely.

    :param str. url: URL that identifies the host and where to find it.
    '''
    _tell = ['attach_interval', 'detach_interval', 'hello', 'stop_actor']
    _ask = ['spawn', 'lookup', 'lookup_url', 'say_hello', 'has_actor']
    _ref = ['spawn', 'lookup', 'lookup_url']

    def __init__(self, url):
        self.actors = {}
        self.threads = {}
        self.pthreads = {}
        self.intervals = {}
        self.locks = {}
        self.url = url
        self.running = False
        self.alive = True
        self.load_transport(url)
        self.init_host()

        self.future_manager = future.FutureManager()

        self.ppool = None
        # self.cleaner = interval_host(get_host(), CLEAN_INT, self.do_clean)

    def hello(self):
        print 'Hello!!'

    def say_hello(self):
        print 'Sending hello.'
        return 'Hello from HOST!!'

    def load_transport(self, url):
        '''
        For remote communication. Sets the communication dispatcher of the host
        at the address and port specified.

        The scheme must be http if using a XMLRPC dispatcher.
        amqp for RabbitMQ communications.

        This methos is internal. Automatically called when creating the host.

        :param str. url: URL where to bind the host. Must be provided in
            the tipical form: 'scheme://address:port/hierarchical_path'
        '''
        aurl = urlparse(url)
        addrl = aurl.netloc.split(':')
        self.addr = addrl[0], addrl[1]
        self.transport = aurl.scheme
        self.host_url = aurl

        if aurl.scheme == 'http':
            self.launch_actor('http', rpcactor.RPCDispatcher(url, self, 'rpc'))

        elif aurl.scheme == 'amqp':
            self.launch_actor('amqp', rpcactor.RPCDispatcher(url, self,
                                                             'rabbit'))

    def spawn(self, aid, klass, param=None):
        '''
        This method creates an actor attached to this host. It will be
        an instance of the class *klass* and it will be assigned an ID
        that identifies it among the host.

        This method can be called remotely synchronously.

        :param str. aid: identifier for the spawning actor. Unique within
            the host.
        :param class klass: class type of the spawning actor. If you are
            spawning remotely and the class is not in the server module,
            you must specify here the path to that class in the form
            'module.py/Class' so the server can import the class and create
            the instance.
        :param list param: arguments for the init function of the
            spawning actor class.
        :return: :class:`~.Proxy` of the actor spawned.
        :raises: :class:`AlreadyExistsError`, if the ID specified is
            already in use.
        :raises: :class:`HostDownError` if the host is not initiated.
        '''
        if param is None:
            param = []
        if not self.alive:
            raise HostDownError()
        if isinstance(klass, basestring):
            module, klass = klass.split('/')
            module_ = __import__(module, globals(), locals(),
                                 [klass], -1)
            klass_ = getattr(module_, klass)
        elif isinstance(klass, (types.TypeType, types.ClassType)):
            klass_ = klass
        url = '%s://%s/%s' % (self.transport, self.host_url.netloc, aid)
        if url in self.actors.keys():
            raise AlreadyExistsError(url)
        else:
            obj = klass_(*param)
            obj.id = aid
            if self.running:
                obj.host = self.proxy
            # else:
            #     obj.host = Exception("Host is not an active actor. \
            #                           Use 'init_host' to make it alive.")

            if hasattr(klass_, '_parallel') and klass_._parallel:
                new_actor = parallels.ActorParallel(url, klass_, obj)
                lock = new_actor.get_lock()
                self.locks[url] = lock
            else:
                new_actor = actor.Actor(url, klass_, obj)

            obj.proxy = Proxy(new_actor)
            self.launch_actor(url, new_actor)
            return Proxy(new_actor)

    def has_actor(self, aid):
        '''
        Checks if the given id is used in the host by some actor.

        :param str. aid: identifier of the actor to check.
        :return: True if the id is used within the host.
        '''
        url = '%s://%s/%s' % (self.transport, self.host_url.netloc, aid)
        return url in self.actors.keys()

    def lookup(self, aid):
        '''
        Gets a new proxy that references to the actor of this host
        (only actors in this host) identified by the given ID.

        This method can be called remotely synchronously.

        :param str. aid: identifier of the actor you want.
        :return: :class:`~.Proxy` of the actor requiered.
        :raises: :class:`NotFoundError`  if the actor does not exist.
        :raises: :class:`HostDownError`  if the host is down.
        '''
        if not self.alive:
            raise HostDownError()
        url = '%s://%s/%s' % (self.transport, self.host_url.netloc, aid)
        if url in self.actors.keys():
            return Proxy(self.actors[url])
        else:
            raise NotFoundError(url)

    def shutdown(self):
        # '''
        # For internal calls.
        # '''
        if self.alive:
            for interval_event in self.intervals.values():
                interval_event.set()

            self.future_manager.stop()

            for actor in self.actors.values():
                Proxy(actor).stop()

            # stop the pool (close & join)
            if self.ppool is not None:
                if core_type == 'thread':
                    self.ppool.close()
                self.ppool.join()

            # By now all pthreads should be gone
            for parall in self.pthreads.keys():
                parall.join()

            for thread in self.threads.keys():
                try:
                    thread.join()
                except Exception, e:
                    print e

            self.locks.clear()
            self.actors.clear()
            self.threads.clear()
            self.pthreads.clear()
            self.running = False
            self.alive = False

            del util.hosts[self.url]
            if util.main_host.url == self.url:
                util.main_host = (util.hosts.values()[0] if util.hosts.values()
                                  else None)

    def stop_actor(self, aid):
        '''
        This method removes one actor from the Host, stoping it and deleting
        all its references.

        :param str. aid: identifier of the actor you want to stop.
        '''
        url = '%s://%s/%s' % (self.transport, self.host_url.netloc, aid)
        if url != self.url:
            actor = self.actors[url]
            Proxy(actor).stop()
            actor.thread.join()
            del self.actors[url]
            del self.threads[actor.thread]

    def lookup_url(self, url, klass, module=None):
        '''
        Gets a proxy reference to the actor indicated by the URL in the
        parameters. It can be a local reference or a remote direction to
        another host.

        This method can be called remotely synchronously.

        :param srt. url: address that identifies an actor.
        :param class klass: the class of the actor.
        :param srt. module: if the actor class is not in the calling module,
            you need to specify the module where it is here. Also, the *klass*
            parameter change to be a string.
        :return: :class:`~.Proxy` of the actor requested.
        :raises: :class:`NotFoundError`, if the URL specified do not
            correspond to any actor in the host.
        :raises: :class:`HostDownError`  if the host is down.
        :raises: :class:`HostError`  if there is an error looking for
            the actor in another server.
        '''
        if not self.alive:
            raise HostDownError()
        aurl = urlparse(url)
        if self.is_local(aurl):
            if url not in self.actors.keys():
                raise NotFoundError(url)
            else:
                return Proxy(self.actors[url])
        else:
            try:
                dispatcher = self.actors[aurl.scheme]
                if module is not None:
                    module_ = __import__(module, globals(), locals(),
                                         [klass], -1)
                    klass_ = getattr(module_, klass)
                elif isinstance(klass, (types.TypeType, types.ClassType)):
                    klass_ = klass
                else:
                    raise HostError("The class specified to look up is" +
                                    " not a class.")
                remote_actor = actor.ActorRef(url, klass_, dispatcher.channel)
                return Proxy(remote_actor)
            except Exception:
                raise HostError("ERROR looking for the actor on another " +
                                "server. Hosts must " +
                                "be in http to work properly.")

    def is_local(self, aurl):
        # '''Private method.
        # Tells if the address given is from this host.
        #
        # :param ParseResult aurl: address to analyze.
        # :return: (*Bool.*) If is local (**True**) or not (**False**).
        # '''
        return self.host_url.netloc == aurl.netloc

    def launch_actor(self, url, actor):
        # '''Private method.
        # This function makes an actor alive to start processing queries.
        #
        # :param str. url: identifier of the actor.
        # :param Actor actor: instance of the actor.
        # '''
        actor.run()
        self.actors[url] = actor
        self.threads[actor.thread] = url

    def init_host(self):
        # '''
        # This method creates an actor for the Host so it can spawn actors
        # remotely. Called always from the init function of the host, so
        # no need for calling this directly.
        # '''
        if not self.running and self.alive:
            self.id = self.url
            host = actor.Actor(self.url, Host, self)
            self.proxy = Proxy(host)
            # self.actors[self.url] = host
            self.launch_actor(self.url, host)
            # host.run()
            # self.threads[host.thread] = self.url
            self.running = True

    def attach_interval(self, interval_id, interval_event):
        '''Registers an interval event to the host.'''
        self.intervals[interval_id] = interval_event

    def detach_interval(self, interval_id):
        '''Deletes an interval event from the host registry.'''
        del self.intervals[interval_id]

    def dumps(self, param):
        '''
        Checks the parameters generating new proxy instances to avoid
        query concurrences from shared proxies and creating proxies for
        actors from another host.
        '''
        if isinstance(param, Proxy):
            filename = sys.modules[param.actor.klass.__module__].__file__
            module_name = os.path.splitext(os.path.basename(filename))[0]
            return ProxyRef(param.actor.url, param.actor.klass.__name__,
                            module_name)
        elif isinstance(param, list):
            return [self.dumps(elem) for elem in param]
        elif isinstance(param, dict):
            new_dict = param
            for key in new_dict.keys():
                new_dict[key] = self.dumps(new_dict[key])
            return new_dict
        else:
            return param

    def loads(self, param):
        '''
        Checks the return parameters generating new proxy instances to
        avoid query concurrences from shared proxies and creating
        proxies for actors from another host.
        '''
        if isinstance(param, ProxyRef):
            try:
                return self.lookup_url(param.url, param.klass, param.module)
            except HostError:
                print "Can't lookup for the actor received with the call. \
                    It does not exist or the url is unreachable.", param
                raise HostError
        elif isinstance(param, list):
            return [self.loads(elem) for elem in param]
        elif isinstance(param, dict):
            new_dict = param
            for key in new_dict.keys():
                new_dict[key] = self.loads(new_dict[key])
            return new_dict
        else:
            return param

    def new_parallel(self, function, *params):
        '''
        Register a new thread executing a parallel method.
        '''
        # Create a pool if not created (processes or Gevent...)
        if self.ppool is None:
            if core_type == 'thread':
                from multiprocessing.pool import ThreadPool
                self.ppool = ThreadPool(50)
            else:
                from gevent.pool import Pool
                self.ppool = Pool(50)
        # Add the new task to the pool
        self.ppool.apply_async(function, *params)


def shutdown(url=None):
    '''
    Stops the Host passed by parameter or all of them if none is
    specified, stopping at the same time all its actors.
    Should be called at the end of its usage, to finish correctly
    all the connections and threads.
    '''
    if url is None:
        for host in util.hosts.values():
            host.shutdown()
        global core_type
        core_type = None
    else:
        host = util.hosts[url]
        host.shutdown()


def signal_handler(signal=None, frame=None):
    # '''
    # This gets the signal of Ctrl+C and stops the host. It also ends
    # the execution. Needs the invocation of :meth:`serve_forever`.
    #
    # :param signal: SIGINT signal interruption sent with a Ctrl+C.
    # :param frame: the current stack frame. (not used)
    # '''
    print 'You pressed Ctrl+C!'
    util.main_host.serving = False
    shutdown(util.main_host.url)


def serve_forever():
    '''
    This allows the host (main host) to keep alive indefinitely so its actors
    can receive queries at any time.
    The main thread stays blocked forever.
    To kill the execution, press Ctrl+C.

    See usage example in :ref:`sample6`.
    '''
    if not util.main_host.alive:
        raise Exception("This host is already shutted down.")
    util.main_host.serving = True
    signal.signal(SIGINT, signal_handler)
    print 'Press Ctrl+C to kill the execution'
    while util.main_host is not None and util.main_host.serving:
        try:
            sleep(1)
        except Exception:
            pass
    print 'BYE!'


def interval(host, time, actor, method, *args, **kwargs):
    '''Creates an Event attached to the host for management that will
    execute the *method* of the *actor* every *time* seconds.

    See example in :ref:`sample_inter`

    :param Proxy host: host that will manage the interval, commonly the
        host of the actor.
    :param int time: seconds for the intervals.
    :param Proxy actor: actor to which make the call every *time* seconds.
    :param Str. method: method of the *actor* to be called.
    :param list args: arguments for *method*.
    :return: :class:`Event` instance of the interval.
    '''
    call = getattr(actor, method, None)
    if not callable(call):
        raise IntervalError("The actor %s does not have the method %s."
                            % (actor.get_id(), method))
    if call.__class__.__name__ in ["TellWrapper", "TellRefWrapper"]:
        # If the method is a normal tell, the interval thread can send
        # the calls normally.
        # It it is a Ref Tell, the proxies in the args would be parsed
        # during the call to this very method. So the call can be made
        # as a normall Tell. The actor will do the loads normally on the
        # receive as it has its methods marked as ref.
        if call.__class__.__name__ is "TellRefWrapper":
            call.__call__ = TellWrapper.__call__

        return intervals.interval_host(host, time, call, *args, **kwargs)
    else:
        raise IntervalError("The callable for the interval must be a tell \
            method of the actor.")


def later(timeout, actor, method, *args, **kwargs):
    '''
    Sets a timer that will call the *method* of the *actor* past *timeout*
    seconds.

    See example in :ref:`sample_inter`

    :param int timeout: seconds until the method is called.
    :param Proxy actor: actor to which make the call after *time* seconds.
    :param Str. method: method of the *actor* to be called.
    :param list args: arguments for *method*.
    :return: manager of the later (Timer in thread,
        Greenlet in green_thread)
    '''
    call = getattr(actor, method, None)
    if not callable(call):
        raise IntervalError("later: The actor %s does not have the method \
                             %s." % (actor.get_id(), method))
    if call.__class__.__name__ in ["TellWrapper", "TellRefWrapper"]:
        # As with the interval, args have already been dumped.
        if call.__class__.__name__ is "TellRefWrapper":
            call.__call__ = TellWrapper.__call__
        return intervals.later(timeout, call, *args, **kwargs)
    else:
        raise IntervalError("The callable for the later must be a tell \
                             method of the actor.")


def sleep(seconds):
    '''
    Facade for the sleep function. Do not use time.sleep if you are
    running green threads.
    '''
    intervals.sleep(seconds)
