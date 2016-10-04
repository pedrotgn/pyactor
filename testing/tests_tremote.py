'''
Remote queries unittest module: python threads core
@author: Daniel Barcelona Pons
'''
import unittest
import sys
import os
import signal

from pyactor.context import *
from pyactor.proxy import *
from pyactor.util import *
import pyactor.context


class Echo(object):
    _tell = ['echo']
    _ask = ['say_something', 'say_something_slow', 'raise_something']

    def echo(self, msg):
        global out
        print msg
        out = msg

    def say_something(self):
        return 'something'

    def say_something_slow(self):
        sleep(2)
        return 'something'

    def raise_something(self):
        sleep(1)
        raise Exception('raising something')


class Bot(object):
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


class TestBasic(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        # self.bu = sys.stdout
        # sys.stdout = open(os.devnull, 'w')
        # self.out = ""
        set_context()
        self.hr = create_host('http://127.0.0.1:1277')
        self.h = self.hr.proxy
        self.e1 = self.h.spawn('echo1', Echo)

    def tearDown(self):
        self.hr.shutdown()
        pyactor.context.core_type = None
        # sys.stdout = self.bu

    def test_1hostbasic(self):
        global out
        out = ""
        host2 = create_host('http://127.0.0.1:1288')
        self.assertEqual(self.hr.actors['http'].__class__, RPCDispatcher)

        with self.assertRaises(HostError):
            h2 = create_host('http://127.0.0.1:1277')
        self.assertEqual(self.hr, get_host())

        host2.proxy.hello()
        response = host2.proxy.say_hello()
        self.assertEqual(response, 'Hello from HOST!!')

        self.e1.echo('1')
        sleep(1)
        self.assertEqual(out, '1')

        host2.shutdown()

    def test_2remotespawn(self):
        global out
        out = ""
        host2 = create_host('http://127.0.0.1:1389')

        e2 = host2.proxy.spawn('echo', 'tests_tremote/Echo')
        e2.echo('1')
        sleep(2)
        # self.assertEqual(out, '1')

        b1 = host2.proxy.spawn('bot1', Bot)
        self.assertEqual(b1.get_name(), 'bot1')
        self.assertEqual(str(b1.get_proxy("h")), str(b1))
        self.assertNotEqual(b1.get_proxy("y"), b1)
        self.assertEqual(str(b1.get_host()), str(host2.proxy))
        self.assertNotEqual(id(b1.get_host()), id(host2.proxy))

        host2.shutdown()


if __name__ == '__main__':
    print ('## Remote WITH THREADS')
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
