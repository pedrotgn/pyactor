'''
unittest module
'''
import unittest, sys
from pyactor.context import *
from pyactor.actor import *
from pyactor.proxy import *
from pyactor.util import *
from pyactor.intervals import *
from time import sleep
import os, signal


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
    _ask = ['get_name','get_proxy','get_host']
    def get_name(self):
        return self.id
    def get_proxy(self):
        return self.proxy
    def get_host(self):
        return self.host
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

class Counter:
    _ask = []
    _tell = ['count', 'init_start']

    def init_start(self):
        self.interval1 = interval_host(self.host, 1, self.count)
        later(5, self.stop_interval)

    def stop_interval(self):
        self.interval1.set()

    def count(self):
        global cnt
        cnt = cnt+1

'''class TestForever(unittest.TestCase):
    def __serve(self):
        self.h=create_host()
        self.h.serve_forever()


    def setUp(self):
        pass
        #self.bu=sys.stdout
        #sys.stdout = open(os.devnull, 'w')
    def test_forever(self):
        t = Thread(target=self.__serve)
        t.start()
        sleep(1)
        os.kill(t.pid, signal.SIGINT)
        t.join()

    def tearDown(self):
        #self.h.shutdown()
        pass
        #sys.stdout = self.bu'''

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.bu=sys.stdout
        sys.stdout = open(os.devnull, 'w')
        #self.out=""
        self.hr=create_host()
        self.h=self.hr.proxy
        self.e1=self.h.spawn('echo1',Echo).get()
    def tearDown(self):
        #check=self.h.sync_shutdown().get(2)
        #self.assertEqual(check, 0)
        self.hr.shutdown()
        #sleep(1)
        sys.stdout = self.bu

    def test_1hostcreation(self):
        self.assertEqual(self.h.__class__.__name__, 'Proxy')
        self.assertEqual(self.h.actor.klass.__name__, 'Host')
        self.assertEqual(self.h.actor.tell, ['attach_interval', 'detach_interval','stop'])
        self.assertEqual(self.h.actor.ask, ['spawn','lookup','spawn_n','lookup_url'])

    def test_2spawning(self):
        global out
        out=""
        self.assertEqual(self.e1.__class__.__name__, 'Proxy')
        self.assertTrue(self.e1.actor.is_alive())

        with self.assertRaises(AlreadyExists):
            e2=self.h.spawn('echo1',Echo).get()

        b1 = self.h.spawn('bot1', Bot).get()
        self.assertEqual(b1.get_name().get(), 'bot1')
        self.assertEqual(str(b1.get_proxy().get()), str(b1))
        self.assertEqual(str(b1.get_host().get()), str(self.h))

        g = self.h.spawn_n(3,'echog',Echo)



    def test_3queries(self):
        global out
        self.assertEqual(self.e1.echo.__class__.__name__,'TellWrapper')
        s=self.e1.echo('hello there!!')
        self.assertEqual(s,None)
        sleep(0.1)
        self.assertEqual(out,'hello there!!')
        ask=self.e1.say_something()
        self.assertEqual(ask.__class__.__name__,'Future')
        self.assertEqual(ask.get(),'something')

        bot = self.h.spawn('bot',Bot).get()
        bot.set_echo(self.e1)
        bot.ping()
        sleep(0.1)
        self.assertEqual(out, 'something')

        with self.assertRaises(Timeout):
            self.e1.say_something_slow().get()

    def test_4lookup(self):
        global out
        e = self.h.lookup('echo1').get()
        self.assertEqual(e.actor.klass.__name__,'Echo')
        self.assertEqual(e.actor,self.e1.actor)
        e.echo('hello')
        sleep(2)
        self.assertEqual(out,'hello')

        with self.assertRaises(NotFound):
            e = self.h.lookup('echo2').get()

        ee = self.h.lookup_url('local://local:6666/echo1', Echo).get()
        self.assertEqual(ee.actor.klass.__name__,'Echo')
        self.assertEqual(ee.actor,self.e1.actor)
        ee.echo('hello')
        sleep(1)
        self.assertEqual(out,'hello')
        with self.assertRaises(NotFound):
            e = self.h.lookup_url('local://local:6666/echo2', Echo).get()

    def test_5shutdown(self):
        self.hr.shutdown()
        #sleep(0.1)
        #Now the actor is not running, invoking a method should raise Timeout.
        with self.assertRaises(Timeout):
            self.e1.say_something().get()
        #The actor should not be alive.
        self.assertFalse(self.e1.actor.is_alive())

    def test_6intervals(self):
        global cnt
        cnt = 0
        c = self.hr.spawn('count', Counter)
        c.init_start()
        sleep(6)
        self.assertEqual(cnt, 5)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
    '''suite = unittest.TestLoader().loadTestsFromTestCase(TestForever)
    unittest.TextTestRunner(verbosity=2).run(suite)'''
