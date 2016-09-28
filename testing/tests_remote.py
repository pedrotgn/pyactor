'''
Remote queries unittest module: python threads core
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
import pyactor.context


class TestBasic(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.bu = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        # self.out = ""
        set_context()
        self.hr = create_host()
        self.h = self.hr.proxy
        # self.e1 = self.h.spawn('echo1', Echo)

    def tearDown(self):
        self.hr.shutdown()
        pyactor.context.core_type = None
        sys.stdout = self.bu

    def test_1hostcreation(self):
        pass


if __name__ == '__main__':
    print ('## Remote WITH THREADS')
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
