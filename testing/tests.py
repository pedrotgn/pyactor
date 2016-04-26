'''
unittest module
'''
import unittest, sys
from pyactor.context import *
from pyactor.actor import *
from pyactor.proxy import *
from pyactor.util import *
from time import sleep


class Echo:
    _tell =['echo']
    _ask = ['say_something','say_something_slow']
    def echo(self,msg):
        global out
        out = msg
    def say_something(self):
        return 'something'
    def say_something_slow(self):
        sleep(2)
        return 'something'

class Bot:
    _tell =['set_echo','ping','pong']
    _ask = []
    def set_echo(self,echo):
        self.echo = echo
    def ping(self):
        future = self.echo.say_something()
        future.add_callback('pong')
        #print 'pinging..'
    def pong(self,msg):
        global out
        out = msg
        #print 'callback',msg

class TestBasic(unittest.TestCase):
    def test_1hostcreation(self):
        global h
        h=init_host()
        self.assertEqual(h.__class__.__name__, 'Proxy')
        self.assertEqual(h.actor.klass.__name__, 'Host')
        self.assertEqual(h.actor.tell, ['shutdown', 'stop'])
        self.assertEqual(h.actor.ask, ['spawn','lookup','spawn_n','lookup_url'])

    def test_2spawning(self):
        global h
        global e1
        r=h.spawn('echo1',Echo)
        e1=r.get()
        self.assertEqual(r.__class__.__name__, 'Future')
        self.assertEqual(e1.__class__.__name__, 'Proxy')
        self.assertTrue(e1.actor.is_alive())

        with self.assertRaises(AlreadyExists):
            e2=h.spawn('echo1',Echo).get()

        self.assertEqual(e1.id, 'echo1')
        e2 = e1.get_proxy()
        self.assertEqual(e2.id, 'echo1')
        self.assertEqual(str(e1),str(e2))

    def test_3queries(self):
        global h
        global e1

        self.assertEqual(e1.echo.__class__.__name__,'TellWrapper')
        s=e1.echo('hello there!!')
        self.assertEqual(s,None)
        global out
        sleep(0.1)
        self.assertEqual(out,'hello there!!')
        ask=e1.say_something()
        self.assertEqual(ask.__class__.__name__,'Future')
        self.assertEqual(ask.get(),'something')

        bot = h.spawn('bot',Bot).get()
        bot.set_echo(e1)
        bot.ping()
        #global out
        sleep(0.1)
        self.assertEqual(out, 'something')

        with self.assertRaises(Timeout):
            e1.say_something_slow().get()

    def test_4lookup(self):
        global h
        global e1
        e = h.lookup('echo1').get()
        self.assertEqual(e.actor.klass.__name__,'Echo')
        self.assertEqual(e.actor,e1.actor)
        e.echo('hello')
        global out
        sleep(1)
        self.assertEqual(out,'hello')

        with self.assertRaises(NotFound):
            e = h.lookup('echo2').get()

        ee = h.lookup_url('local://local:6666/echo1', Echo).get()
        self.assertEqual(ee.actor.klass.__name__,'Echo')
        self.assertEqual(ee.actor,e1.actor)
        ee.echo('hello')
        #global out
        sleep(1)
        self.assertEqual(out,'hello')
        with self.assertRaises(NotFound):
            e = h.lookup_url('local://local:6666/echo2', Echo).get()

    def test_5shutdown(self):
        global h
        global e1
        h.shutdown()
        sleep(0.1)
        #Now the actor is not running, invoking a method should raise Timeout.
        with self.assertRaises(Timeout):
            e1.say_something().get()
        #The actor should not be alive.
        self.assertFalse(e1.actor.is_alive())



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
