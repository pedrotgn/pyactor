'''
Local queries unittest module: python threads core
@author: Daniel Barcelona Pons
'''
import unittest
import sys
# from time import sleep
import os
import signal

from pyactor.context import *
from pyactor.proxy import *
from pyactor.util import *
from pyactor.exceptions import *
import pyactor.context


class Echo:
    _tell = ['echo']
    _ask = ['say_something', 'say_something_slow', 'raise_something']

    def echo(self, msg):
        global out
        out = msg

    def say_something(self):
        return 'something'

    def say_something_slow(self):
        sleep(2)
        return 'something'

    def raise_something(self):
        sleep(1)
        raise Exception('raising something')


class Bot:
    _tell = ['set_echo', 'ping', 'pong', 'multiping']
    _ask = ['get_name', 'get_proxy', 'get_host', 'get_echo', 'get_echo_ref',
            'check_ref', 'get_real_host']
    _ref = ['get_name', 'set_echo', 'get_proxy', 'get_host', 'get_echo_ref',
            'check_ref', 'multiping']

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
        future = self.echo.say_something(future=True)
        future.add_callback('pong')
        # print 'pinging..'

    def multiping(self, bot=None):
        future = self.echo.say_something(future=True)
        # print 'pinging..'
        if bot is not None:
            future.add_callback('pong', bot)
            future.add_callback('pong', bot)
        future.add_callback('pong')
        sleep(1)
        # print 'late callback:'
        future.add_callback('pong')

    def pong(self, future):
        global out
        global cnt
        cnt += 1
        msg = future.result()
        if future.exception() is None:
            out = msg
        # print 'callback', msg

    def get_real_host(self):
        return get_host()


class Counter:
    _ask = []
    _tell = ['count', 'init_start', 'stop_interval']

    def init_start(self):
        self.interval1 = interval(self.host, 1, self.proxy, "count")
        later(4, self.proxy, "stop_interval")

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
        return self.server.download(filename, timeout=10)


class WebF(object):
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
        future = self.server.download(filename, future=True)
        return future.result(6)


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
        return self.server.download(filename, timeout=10)


class Workload(object):
    _ask = []
    _tell = ['launch', 'download', 'remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        global cnt
        for i in range(10):
            try:
                print self.server.list_files(timeout=2)
            except TimeoutError as e:
                cnt = 1000
                raise TimeoutError

    def remote_server(self, web_server):
        self.server = web_server

    def download(self):
        self.server.get_file('a1.txt', timeout=10)
        print 'download finished'


class TestBasic(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.bu = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        # self.out = ""
        set_context()
        self.h = create_host()
        self.e1 = self.h.spawn('echo1', Echo)

    def tearDown(self):
        shutdown()
        # sleep(1)
        sys.stdout = self.bu

    def test_1hostcreation(self):
        self.assertEqual(self.h.__class__.__name__, 'Proxy')
        self.assertEqual(self.h.actor.klass.__name__, 'Host')
        self.assertEqual(self.h.actor.tell, ['attach_interval',
                                             'detach_interval', 'hello',
                                             'stop_actor', 'stop'])
        self.assertEqual(self.h.actor.ask, ['say_hello', 'has_actor'])
        self.assertEqual(self.h.actor.ask_ref, ['spawn', 'lookup',
                                                'lookup_url'])
        with self.assertRaises(Exception):
            h2 = create_host()
        self.assertEqual(self.h.actor._obj, get_host())

        b1 = self.h.spawn('bot1', Bot)
        self.assertEqual(self.h.actor._obj, b1.get_real_host())

        h2 = create_host("local://local:7777/host")
        with self.assertRaises(HostError):
            # This line raise Exception in actor's thread for not http hosts
            b2 = h2.spawn('bot1', Bot)
        # self.assertEqual(h2, b2.get_real_host())
        # with self.assertRaises(Exception):
        #     b2.set_echo(self.e1)
        #     b1.set_echo(b2)
        # This lines raise Exception in actor's thread for not http hosts

    def test_2spawning(self):
        # global out
        # out = ""
        self.assertEqual(self.e1.__class__.__name__, 'Proxy')
        self.assertTrue(self.e1.actor.is_alive())

        with self.assertRaises(AlreadyExistsError):
            e2 = self.h.spawn('echo1', Echo)

        b1 = self.h.spawn('bot1', Bot)
        self.assertEqual(b1.get_name(), 'bot1')
        self.assertEqual(str(b1.get_proxy("h")), str(b1))
        self.assertEqual(b1.get_proxy("y"), b1)
        self.assertEqual(str(b1.get_host()), str(self.h))
        self.assertNotEqual(id(b1.get_host()), id(self.h))

        self.assertEqual(b1.check_ref([{'e': self.e1}])[0]['e'], self.e1)
        future = b1.check_ref(self.e1, future=True)
        self.assertEqual(future.result(), self.e1)

    def test_3queries(self):
        global out
        global cnt
        out = ""
        cnt = 0
        self.assertEqual(self.e1.echo.__class__.__name__, 'TellWrapper')
        s = self.e1.echo('hello there!!')
        sleep(0.1)
        self.assertEqual(s, None)
        self.assertEqual(out, 'hello there!!')

        ask = self.e1.say_something(future=True)
        self.assertEqual(ask.__class__.__name__, 'Future')
        self.assertEqual(ask.result(1), 'something')
        self.assertTrue(ask.done())

        ask = self.e1.raise_something(future=True)
        self.assertTrue(ask.running())
        self.assertFalse(ask.done())
        with self.assertRaises(Exception):
            ask.send_work()
        with self.assertRaises(TimeoutError):
            ask.exception(0.2)
        with self.assertRaises(TimeoutError):
            ask.result(0.2)
        self.assertEqual(ask.__class__.__name__, 'Future')
        self.assertEqual(ask.exception(1).__str__(), 'raising something')
        with self.assertRaises(Exception):
            self.assertEqual(ask.result(1), 'something')
        self.assertTrue(ask.done())
        self.assertFalse(ask.running())

        bot = self.h.spawn('bot', Bot)
        bot.set_echo(self.e1)
        sleep(0.1)
        self.assertNotEqual(self.e1, bot.get_echo())
        self.assertNotEqual(bot.get_echo(), bot.get_echo_ref())
        bot.ping()
        sleep(1)
        self.assertEqual(out, 'something')

        bot2 = self.h.spawn('bot2', Bot)
        bot.multiping(bot2)
        sleep(2)
        self.assertEqual(out, 'something')
        self.assertEqual(cnt, 5)

        with self.assertRaises(TimeoutError):
            self.e1.say_something_slow()

        with self.assertRaises(Exception):
            ask.uppercase()

    def test_4lookup(self):
        global out
        e = self.h.lookup('echo1')
        self.assertEqual(e.actor.klass.__name__, 'Echo')
        self.assertEqual(e.actor, self.e1.actor)  # !!!!!
        self.assertEqual(e, self.e1)
        e.echo('hello')
        sleep(2)
        self.assertEqual(out, 'hello')

        with self.assertRaises(NotFoundError):
            e = self.h.lookup('echo2')

        ee = self.h.lookup_url('local://local:6666/echo1', Echo)
        self.assertEqual(ee.actor.klass.__name__, 'Echo')
        self.assertEqual(ee.actor, self.e1.actor)
        self.assertEqual(ee, self.e1)
        ee.echo('hello')
        sleep(1)
        self.assertEqual(out, 'hello')
        with self.assertRaises(NotFoundError):
            e = self.h.lookup_url('local://local:6666/echo2', Echo)

    def test_5shutdown(self):
        shutdown()
        # sleep(0.1)
        self.assertEqual(get_host(), None)
        with self.assertRaises(HostError):
            self.h.lookup('echo1')
        with self.assertRaises(HostError):
            self.h.lookup_url('local://local:6666/echo1', Echo)
        with self.assertRaises(HostError):
            self.h.spawn('bot', Bot)
        # Now the actor is not running, invoking a method should raise Timeout.
        with self.assertRaises(TimeoutError):
            self.e1.say_something()
        # The actor should not be alive.
        self.assertFalse(self.e1.actor.is_alive())

    def test_6intervals(self):
        global cnt
        cnt = 0
        c = self.h.spawn('count', Counter)
        c.init_start()
        sleep(6)
        self.assertEqual(cnt, 4)

    def test_7parallels(self):
        global cnt
        cnt = 0
        f1 = self.h.spawn('file1', File)
        web = self.h.spawn('web1', Web)
        web.remote_server(f1)
        load = self.h.spawn('wl1', Workload)
        self.assertEqual(web.actor.__class__.__name__, 'ActorParallel')
        load.remote_server(web)
        load2 = self.h.spawn('wl2', Workload)
        load2.remote_server(web)
        load.launch()
        load2.download()
        sleep(7)

        self.assertNotEqual(cnt, 1000)

        sleep(1)

        web2 = self.h.spawn('web2', WebNP)
        web2.remote_server(f1)
        self.assertNotEqual(web2.actor.__class__.__name__, 'ActorParallel')
        load.remote_server(web2)
        load2.remote_server(web2)

        load.launch()
        load2.download()
        sleep(7)

        self.assertEqual(cnt, 1000)

        sleep(1)
        cnt = 0
        web3 = self.h.spawn('web3', WebF)
        web3.remote_server(f1)
        load.remote_server(web3)
        load2.remote_server(web3)
        load.launch()
        load2.download()
        sleep(7)

        self.assertNotEqual(cnt, 1000)

    def test_checklist(self):
        w = self.h.spawn('web', Web)
        self.assertEqual(w.actor.tell, ['stop'])
        self.assertEqual(w.actor.ask, ['list_files', 'get_file'])
        self.assertEqual(w.actor.tell_ref, ['remote_server'])
        self.assertEqual(w.actor.ask_ref, [])
        self.assertEqual(w.actor.tell_parallel, ['remote_server'])
        self.assertEqual(w.actor.ask_parallel, ['list_files', 'get_file'])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
