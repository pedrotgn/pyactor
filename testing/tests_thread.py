'''
unittest module
'''
import unittest
import sys
# from time import sleep
import os
import signal

from pyactor.context import *
from pyactor.proxy import *
from pyactor.util import *
import pyactor.context


class Echo:
    _tell = ['echo']
    _ask = ['say_something', 'say_something_slow']

    def echo(self, msg):
        global out
        out = msg

    def say_something(self):
        return 'something'

    def say_something_slow(self):
        sleep(2)
        return 'something'


class Bot:
    _tell = ['set_echo', 'ping', 'pong']
    _ask = ['get_name', 'get_proxy', 'get_host', 'get_echo', 'get_echo_ref',
            'check_ref', 'get_real_host']
    _ref = ['get_name', 'set_echo', 'get_proxy', 'get_host', 'get_echo_ref',
            'check_ref']

    def get_name(self):
        return self.id

    def get_proxy(self, yo):
        return self.proxy

    def get_host(self):
        return self.host

    def set_echo(self, echo):
        self.echo = echo

    def get_echo(self):
        return self.echo

    def get_echo_ref(self):
        return self.echo

    def check_ref(self, ref):
        return ref

    def ping(self):
        future = self.echo.say_something()
        future.add_callback('pong')
        # print 'pinging..'

    def pong(self, msg):
        global out
        out = msg
        # print 'callback',msg

    def get_real_host(self):
        return get_host()


class Counter:
    _ask = []
    _tell = ['count', 'init_start']

    def init_start(self):
        self.interval1 = interval_host(self.host, 1, self.count)
        later(4, self.stop_interval)

    def stop_interval(self):
        self.interval1.set()

    def count(self):
        global cnt
        if cnt != 4:
            cnt += 1


class File(object):
    _ask = ['download']
    _tell = []

    def download(self, filename):
        print 'downloading ' + filename
        sleep(5)
        return True


class Web(object):
    _ask = ['list_files', 'get_file']
    _tell = ['remote_server']
    _parallel = ['list_files', 'remote_server', 'get_file']
    _ref = ["remote_server"]

    def __init__(self):
        self.files = ['a1.txt', 'a2.txt', 'a3.txt', 'a4.zip']

    def remote_server(self, file_server):
        self.server = file_server

    def list_files(self):
        return self.files

    def get_file(self, filename):
        return self.server.download(filename).get(10)


class WebNP(object):
    _ask = ['list_files', 'get_file']
    _tell = ['remote_server']
    # _parallel = ['get_file']
    _ref = ["remote_server"]

    def __init__(self):
        self.files = ['a1.txt', 'a2.txt', 'a3.txt', 'a4.zip']

    def remote_server(self, file_server):
        self.server = file_server

    def list_files(self):
        return self.files

    def get_file(self, filename):
        return self.server.download(filename).get(10)


class Workload(object):
    _ask = []
    _tell = ['launch', 'download', 'remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        global cnt
        for i in range(10):
            try:
                print self.server.list_files().get(1)
            except TimeoutError as e:
                cnt = 1000
                raise TimeoutError

    def remote_server(self, web_server):
        self.server = web_server

    def download(self):
        self.server.get_file('a1.txt').get(10)
        print 'download finished'


class TestBasic(unittest.TestCase):
    def setUp(self):
        self.bu = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        # self.out = ""
        set_context()
        self.hr = create_host()
        self.h = self.hr.proxy
        self.e1 = self.h.spawn('echo1', Echo).get()

    def tearDown(self):
        self.hr.shutdown()
        pyactor.context.core_type = None
        # sleep(1)
        sys.stdout = self.bu

    def test_1hostcreation(self):
        self.assertEqual(self.hr.__class__.__name__, 'Host')
        self.assertEqual(self.h.__class__.__name__, 'Proxy')
        self.assertEqual(self.h.actor.klass.__name__, 'Host')
        self.assertEqual(self.h.actor.tell, ['attach_interval',
                                             'detach_interval', 'stop'])
        self.assertEqual(self.h.actor.ask, ['spawn', 'lookup', 'spawn_n',
                                            'lookup_url'])
        with self.assertRaises(Exception):
            h2 = create_host()
        self.assertEqual(self.hr, get_host())

        b1 = self.hr.spawn('bot1', Bot)
        self.assertEqual(self.hr, b1.get_real_host().get())

        h2 = create_host("local://local:7777/host")
        b2 = h2.spawn('bot1', Bot)
        self.assertEqual(h2, b2.get_real_host().get())
        b2.set_echo(self.e1)
        with self.assertRaises(Exception):
            b1.set_echo(b2)  # This line raises TCPthing

        h2.shutdown()

    def test_2spawning(self):
        global out
        out = ""
        self.assertEqual(self.e1.__class__.__name__, 'Proxy')
        self.assertTrue(self.e1.actor.is_alive())

        with self.assertRaises(AlreadyExistsError):
            e2 = self.h.spawn('echo1', Echo).get()

        b1 = self.h.spawn('bot1', Bot).get()
        self.assertEqual(b1.get_name().get(), 'bot1')
        self.assertEqual(str(b1.get_proxy("h").get()), str(b1))
        self.assertNotEqual(b1.get_proxy("y").get(), b1)
        self.assertEqual(str(b1.get_host().get()), str(self.h))
        self.assertNotEqual(id(b1.get_host().get()), id(self.h))

        self.assertNotEqual(b1.check_ref([{'e': self.e1}]).get()[0]['e'],
                            self.e1)

    def test_3queries(self):
        global out
        self.assertEqual(self.e1.echo.__class__.__name__, 'TellWrapper')
        s = self.e1.echo('hello there!!')
        self.assertEqual(s, None)
        sleep(0.1)
        self.assertEqual(out, 'hello there!!')
        ask = self.e1.say_something()
        self.assertEqual(ask.__class__.__name__, 'Future')
        self.assertEqual(ask.get(), 'something')

        bot = self.h.spawn('bot', Bot).get()
        bot.set_echo(self.e1)
        self.assertNotEqual(self.e1, bot.get_echo().get())
        self.assertNotEqual(bot.get_echo().get(), bot.get_echo_ref().get())
        bot.ping()
        sleep(1)
        self.assertEqual(out, 'something')

        with self.assertRaises(TimeoutError):
            self.e1.say_something_slow().get()

        with self.assertRaises(Exception):
            ask.uppercase()

    def test_4lookup(self):
        global out
        e = self.h.lookup('echo1').get()
        self.assertEqual(e.actor.klass.__name__, 'Echo')
        self.assertEqual(e.actor, self.e1.actor)  # !!!!!
        self.assertNotEqual(e, self.e1)
        e.echo('hello')
        sleep(2)
        self.assertEqual(out, 'hello')

        with self.assertRaises(NotFoundError):
            e = self.h.lookup('echo2').get()

        ee = self.h.lookup_url('local://local:6666/echo1').get()
        self.assertEqual(ee.actor.klass.__name__, 'Echo')
        self.assertEqual(ee.actor, self.e1.actor)
        self.assertNotEqual(ee, self.e1)
        ee.echo('hello')
        sleep(1)
        self.assertEqual(out, 'hello')
        with self.assertRaises(NotFoundError):
            e = self.h.lookup_url('local://local:6666/echo2').get()

    def test_5shutdown(self):
        self.hr.shutdown()
        # sleep(0.1)
        self.assertEqual(get_host(), None)
        with self.assertRaises(HostDownError):
            self.hr.spawn('bot', Bot)
        with self.assertRaises(HostDownError):
            self.hr.lookup('echo1').get()
        with self.assertRaises(HostDownError):
            self.hr.lookup_url('local://local:6666/echo1')
        with self.assertRaises(TimeoutError):
            self.h.spawn('bot', Bot).get()
        # Now the actor is not running, invoking a method should raise Timeout.
        with self.assertRaises(TimeoutError):
            self.e1.say_something().get()
        # The actor should not be alive.
        self.assertFalse(self.e1.actor.is_alive())

    def test_6intervals(self):
        global cnt
        cnt = 0
        c = self.hr.spawn('count', Counter)
        c.init_start()
        sleep(6)
        self.assertEqual(cnt, 4)

    def test_7parallels(self):
        global cnt
        f1 = self.hr.spawn('file1', File)
        web = self.hr.spawn('web1', Web)
        web.remote_server(f1)
        load = self.hr.spawn('wl1', Workload)
        self.assertEqual(web.actor.__class__.__name__, 'ActorParallel')
        load.remote_server(web)
        load2 = self.hr.spawn('wl2', Workload)
        load2.remote_server(web)
        load.launch()
        load2.download()
        sleep(10)

        self.assertNotEqual(cnt, 1000)

        web2 = self.hr.spawn('web2', WebNP)
        web2.remote_server(f1)
        self.assertNotEqual(web2.actor.__class__.__name__, 'ActorParallel')
        load.remote_server(web2)
        load2.remote_server(web2)

        load.launch()
        load2.download()
        sleep(10)

        self.assertEqual(cnt, 1000)

    def test_checklist(self):
        w = self.hr.spawn('web', Web)
        self.assertEqual(w.actor.tell, ['stop'])
        self.assertEqual(w.actor.ask, ['list_files', 'get_file'])
        self.assertEqual(w.actor.tell_ref, ['remote_server'])
        self.assertEqual(w.actor.ask_ref, [])
        self.assertEqual(w.actor.tell_parallel, ['remote_server'])
        self.assertEqual(w.actor.ask_parallel, ['list_files', 'get_file'])
