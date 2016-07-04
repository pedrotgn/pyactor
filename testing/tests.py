'''
unittest module
'''
import unittest
import sys
# from time import sleep
import os
import signal

import tests_thread
import tests_gevent

if __name__ == '__main__':
    print ('## WITH THREADS')
    suite = unittest.TestLoader().loadTestsFromTestCase(tests_thread.TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print ('## WITH GREEN THREADS')
    suite = unittest.TestLoader().loadTestsFromTestCase(tests_gevent.TestBasic)
    unittest.TextTestRunner(verbosity=2).run(suite)
